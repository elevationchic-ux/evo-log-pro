/**
 * Client-side IndexedDB engine for Offline-First PWA data persistence.
 * Allows operators (dockers, yard crane operators, drivers) to record entries offline.
 */

const DB_NAME = "evo_log_offline_db";
const DB_VERSION = 1;

export interface SyncQueueItem {
  id?: number;
  url: string;
  method: "POST" | "PUT" | "DELETE" | "PATCH";
  payload: any;
  timestamp: number;
  retryCount: number;
}

export function openOfflineDatabase(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    if (typeof window === "undefined" || !("indexedDB" in window)) {
      return reject(new Error("IndexedDB not supported"));
    }

    const request = indexedDB.open(DB_NAME, DB_VERSION);

    request.onupgradeneeded = (event) => {
      const db = (event.target as IDBOpenDBRequest).result;

      if (!db.objectStoreNames.contains("sync_queue")) {
        db.createObjectStore("sync_queue", {
          keyPath: "id",
          autoIncrement: true,
        });
      }

      if (!db.objectStoreNames.contains("offline_cache")) {
        db.createObjectStore("offline_cache", { keyPath: "key" });
      }
    };

    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}

export async function enqueueOfflineAction(
  url: string,
  method: "POST" | "PUT" | "DELETE" | "PATCH",
  payload: any
): Promise<number> {
  const db = await openOfflineDatabase();
  return new Promise((resolve, reject) => {
    const tx = db.transaction("sync_queue", "readwrite");
    const store = tx.objectStore("sync_queue");
    const item: SyncQueueItem = {
      url,
      method,
      payload,
      timestamp: Date.now(),
      retryCount: 0,
    };
    const req = store.add(item);
    req.onsuccess = () => resolve(req.result as number);
    req.onerror = () => reject(req.error);
  });
}
