import { openOfflineDatabase, SyncQueueItem } from "./db";

/**
 * Synchronizer engine for processing enqueued offline actions once connection is restored.
 */
export async function flushOfflineSyncQueue(): Promise<{
  processed: number;
  failed: number;
}> {
  if (typeof window === "undefined" || !navigator.onLine) {
    return { processed: 0, failed: 0 };
  }

  const db = await openOfflineDatabase();
  const tx = db.transaction("sync_queue", "readwrite");
  const store = tx.objectStore("sync_queue");

  return new Promise((resolve) => {
    const getAllReq = store.getAll();
    getAllReq.onsuccess = async () => {
      const items: SyncQueueItem[] = getAllReq.result;
      let processed = 0;
      let failed = 0;

      for (const item of items) {
        try {
          const res = await fetch(item.url, {
            method: item.method,
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(item.payload),
          });

          if (res.ok) {
            // Delete item from queue
            const delTx = db.transaction("sync_queue", "readwrite");
            delTx.objectStore("sync_queue").delete(item.id!);
            processed++;
          } else {
            failed++;
          }
        } catch (err) {
          failed++;
        }
      }

      resolve({ processed, failed });
    };

    getAllReq.onerror = () => resolve({ processed: 0, failed: 0 });
  });
}
