/**
 * offlineSync.ts  Offline Outbox Pattern for EVO-LOG field operations.
 *
 * Designed for Cameroon transit corridors with intermittent connectivity:
 *   • Autoroute Douala-Yaoundé
 *   • Axe Nord (Ngaoundéré)
 *   • Passage frontalier Tchad/RCA
 *
 * Operations that can be queued offline:
 *   - Tickets carburant (fuel vouchers)
 *   - Signatures ePOD (proof of delivery)
 *   - Signalement QHSE (incident/breakdown reports)
 *   - Pointage chauffeur (driver check-in/check-out)
 *
 * Strategy:
 *   1. On action: save to IndexedDB (persistent, survives app restart)
 *   2. On reconnect: replay queue in FIFO order, retry 3× with exp backoff
 *   3. On success: remove from queue, emit 'synced' event
 *   4. On permanent fail (after 3 retries): mark as FAILED, notify user
 */

import { getAccessToken, getApiBaseUrl, tryRefreshToken } from '@/lib/api-client';

export type OfflineOpType =
  | 'TICKET_CARBURANT'
  | 'EPOD_SIGNATURE'
  | 'QHSE_INCIDENT'
  | 'POINTAGE_CHAUFFEUR'
  | 'PANNE_VEHICULE'
  | 'GENERIC_POST';

export type OfflineOpStatus = 'PENDING' | 'SYNCING' | 'SYNCED' | 'FAILED';

export interface OfflineOperation {
  id: string;
  type: OfflineOpType;
  endpoint: string;            // API path to POST to on reconnect
  payload: Record<string, unknown>;
  company_id: number;
  user_id: string;
  created_at: string;          // ISO timestamp
  attempt_count: number;       // how many sync attempts made
  status: OfflineOpStatus;
  error?: string;
}

// ─── IndexedDB setup ───────────────────────────────────────────────────────

const DB_NAME = 'evo-log-offline';
const STORE_NAME = 'outbox';
const DB_VERSION = 1;

function openDB(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open(DB_NAME, DB_VERSION);
    req.onupgradeneeded = (e) => {
      const db = (e.target as IDBOpenDBRequest).result;
      if (!db.objectStoreNames.contains(STORE_NAME)) {
        const store = db.createObjectStore(STORE_NAME, { keyPath: 'id' });
        store.createIndex('status', 'status', { unique: false });
        store.createIndex('company_id', 'company_id', { unique: false });
      }
    };
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
  });
}

function generateId(): string {
  return `offline-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
}

// ─── Outbox queue operations ────────────────────────────────────────────────

export async function enqueueOperation(
  op: Omit<OfflineOperation, 'id' | 'created_at' | 'attempt_count' | 'status'>
): Promise<string> {
  const db = await openDB();
  const id = generateId();
  const record: OfflineOperation = {
    ...op,
    id,
    created_at: new Date().toISOString(),
    attempt_count: 0,
    status: 'PENDING',
  };
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, 'readwrite');
    tx.objectStore(STORE_NAME).add(record);
    tx.oncomplete = () => {
      console.info(`[OfflineSync] Queued ${op.type}  ID: ${id}`);
      window.dispatchEvent(new CustomEvent('offline-queue-updated'));
      resolve(id);
    };
    tx.onerror = () => reject(tx.error);
  });
}

export async function getPendingOperations(): Promise<OfflineOperation[]> {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, 'readonly');
    const index = tx.objectStore(STORE_NAME).index('status');
    const req = index.getAll('PENDING');
    req.onsuccess = () => resolve(req.result || []);
    req.onerror = () => reject(req.error);
  });
}

export async function getAllOperations(): Promise<OfflineOperation[]> {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, 'readonly');
    const req = tx.objectStore(STORE_NAME).getAll();
    req.onsuccess = () => resolve(req.result || []);
    req.onerror = () => reject(req.error);
  });
}

async function updateOperation(id: string, updates: Partial<OfflineOperation>): Promise<void> {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, 'readwrite');
    const store = tx.objectStore(STORE_NAME);
    const getReq = store.get(id);
    getReq.onsuccess = () => {
      const record = { ...getReq.result, ...updates };
      store.put(record);
    };
    tx.oncomplete = () => resolve();
    tx.onerror = () => reject(tx.error);
  });
}

async function deleteOperation(id: string): Promise<void> {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, 'readwrite');
    tx.objectStore(STORE_NAME).delete(id);
    tx.oncomplete = () => resolve();
    tx.onerror = () => reject(tx.error);
  });
}

// ─── Sync engine ────────────────────────────────────────────────────────────

const MAX_RETRIES = 3;

async function syncOperation(op: OfflineOperation, baseUrl: string): Promise<void> {
  const base = baseUrl || getApiBaseUrl();

  // Sans token, le POST échouerait à coup sûr (401) : on garde l'opération en
  // file plutot que de la marquer FAILED pour une raison sans rapport avec sa
  // validité métier. La synchronisation réessaiera au prochain retour en ligne.
  let token = getAccessToken();
  if (!token) {
    const refreshed = await tryRefreshToken();
    token = refreshed ? getAccessToken() : null;
  }
  if (!token) {
    await updateOperation(op.id, { status: 'PENDING' });
    console.warn(`[OfflineSync] ${op.type} en attente : aucune session authentifiée.`);
    return;
  }

  await updateOperation(op.id, { status: 'SYNCING', attempt_count: op.attempt_count + 1 });

  for (let attempt = 0; attempt <= MAX_RETRIES; attempt++) {
    try {
      const response = await fetch(`${base}${op.endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          ...op.payload,
          _offline_id: op.id,
          _synced_at: new Date().toISOString(),
        }),
      });

      if (response.ok) {
        await deleteOperation(op.id);
        console.info(`[OfflineSync] ✅ Synced ${op.type}  ID: ${op.id}`);
        window.dispatchEvent(new CustomEvent('offline-op-synced', { detail: { id: op.id, type: op.type } }));
        return;
      }

      // Token expire entre-temps : on le rafraichit une fois et on retente,
      // sinon la file mourrait en FAILED sur une simple expiration de session.
      if (response.status === 401 && attempt === 0) {
        const refreshed = await tryRefreshToken();
        if (refreshed) {
          token = getAccessToken() || token;
          throw new Error('Session rafraîchie, nouvelle tentative');
        }
        await updateOperation(op.id, { status: 'FAILED', error: '401 : session expirée, reconnexion requise' });
        console.error(`[OfflineSync] ❌ ${op.id} bloqué par la session expirée`);
        return;
      }

      // 4xx errors are permanent failures  no point retrying
      if (response.status >= 400 && response.status < 500) {
        const errText = await response.text();
        await updateOperation(op.id, { status: 'FAILED', error: errText });
        console.error(`[OfflineSync] ❌ Permanent fail for ${op.id}: ${response.status}`);
        return;
      }

      throw new Error(`Server error ${response.status}`);
    } catch (err) {
      const isLastAttempt = attempt === MAX_RETRIES;
      if (isLastAttempt) {
        const errMsg = err instanceof Error ? err.message : String(err);
        await updateOperation(op.id, { status: 'FAILED', error: errMsg });
        console.error(`[OfflineSync] ❌ Max retries reached for ${op.id}: ${errMsg}`);
        return;
      }
      // Exponential backoff: 1s, 2s, 4s
      const delay = Math.pow(2, attempt) * 1000;
      console.warn(`[OfflineSync] Retry ${attempt + 1}/${MAX_RETRIES} in ${delay}ms for ${op.id}`);
      await new Promise((r) => setTimeout(r, delay));
    }
  }
}

/**
 * Replay all pending operations in FIFO order.
 * Call this when navigator.onLine becomes true or on app startup.
 * baseUrl vide => base de l'API resolue depuis api-client (jamais l'origine du
 * frontend : les endpoints en file commencent par /api/v1/...).
 */
export async function syncOutbox(baseUrl: string = ''): Promise<{ synced: number; failed: number }> {
  const pending = await getPendingOperations();
  if (pending.length === 0) return { synced: 0, failed: 0 };

  console.info(`[OfflineSync] 🔄 Syncing ${pending.length} queued operation(s)...`);

  let synced = 0;
  let failed = 0;

  // Process in FIFO order (sort by created_at)
  const sorted = [...pending].sort((a, b) => a.created_at.localeCompare(b.created_at));

  for (const op of sorted) {
    await syncOperation(op, baseUrl);
    const updated = await getAllOperations();
    const result = updated.find((o) => o.id === op.id);
    if (!result) synced++;       // deleted = success
    else if (result.status === 'FAILED') failed++;
  }

  window.dispatchEvent(new CustomEvent('offline-queue-updated'));
  console.info(`[OfflineSync] Sync complete  ✅ ${synced} synced, ❌ ${failed} failed`);
  return { synced, failed };
}

// ─── Auto-sync on reconnect ─────────────────────────────────────────────────

let _syncListenerInstalled = false;

export function installAutoSync(baseUrl: string = ''): () => void {
  if (_syncListenerInstalled) return () => {};
  _syncListenerInstalled = true;

  const handleOnline = async () => {
    console.info('[OfflineSync] 🌐 Network restored  starting outbox sync...');
    await syncOutbox(baseUrl);
  };

  window.addEventListener('online', handleOnline);

  // Also try syncing on startup if online
  if (navigator.onLine) {
    setTimeout(() => syncOutbox(baseUrl), 2000);
  }

  return () => {
    window.removeEventListener('online', handleOnline);
    _syncListenerInstalled = false;
  };
}

// ─── Convenience helpers ────────────────────────────────────────────────────

export function queueTicketCarburant(
  data: { vehicule_id: number; litres: number; montant: number; chauffeur_id: number },
  context: { company_id: number; user_id: string }
) {
  return enqueueOperation({
    type: 'TICKET_CARBURANT',
    endpoint: '/api/v1/transport/carburant/tickets',
    payload: data,
    ...context,
  });
}

export function queueEpodSignature(
  data: { mission_id: number; signature_base64: string; gps_lat?: number; gps_lon?: number; notes?: string },
  context: { company_id: number; user_id: string }
) {
  return enqueueOperation({
    type: 'EPOD_SIGNATURE',
    endpoint: '/api/v1/transport/missions/epod',
    payload: data,
    ...context,
  });
}

export function queueQHSEIncident(
  data: { type_incident: string; description: string; localisation?: string; gps_lat?: number; gps_lon?: number },
  context: { company_id: number; user_id: string }
) {
  return enqueueOperation({
    type: 'QHSE_INCIDENT',
    endpoint: '/api/v1/incidents',
    payload: data,
    ...context,
  });
}

export function queuePanneVehicule(
  data: { vehicule_id: number; description: string; gps_lat?: number; gps_lon?: number },
  context: { company_id: number; user_id: string }
) {
  return enqueueOperation({
    type: 'PANNE_VEHICULE',
    endpoint: '/api/v1/transport/pannes',
    payload: data,
    ...context,
  });
}

export function getQueueCount(): Promise<number> {
  return getPendingOperations().then((ops) => ops.length);
}
