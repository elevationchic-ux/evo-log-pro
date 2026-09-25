'use client';

/**
 * OfflineSyncIndicator.tsx
 * 
 * Visual indicator for offline queue status in the ModuleHeader.
 * Shows:
 *  - 🟢 En ligne (online, queue empty)
 *  - 🟡 N opérations en attente (online but queue has items)
 *  - 🔴 Hors ligne - X opérations en file (offline, with count)
 * 
 * Clicking opens a mini-panel showing queued operations.
 */

import React, { useEffect, useState, useCallback } from 'react';
import { getAllOperations, syncOutbox, installAutoSync, type OfflineOperation } from '@/utils/offlineSync';

interface OfflineSyncIndicatorProps {
  baseUrl?: string;
  companyId?: number;
}

export default function OfflineSyncIndicator({ baseUrl = '', companyId }: OfflineSyncIndicatorProps) {
  const [isOnline, setIsOnline] = useState(true);
  const [operations, setOperations] = useState<OfflineOperation[]>([]);
  const [isSyncing, setIsSyncing] = useState(false);
  const [showPanel, setShowPanel] = useState(false);
  const [mounted, setMounted] = useState(false);

  const refreshQueue = useCallback(async () => {
    try {
      const ops = await getAllOperations();
      setOperations(ops);
    } catch {
      // IndexedDB not available in SSR
    }
  }, []);

  useEffect(() => {
    setMounted(true);
    setIsOnline(navigator.onLine);
    refreshQueue();

    const handleOnline = () => { setIsOnline(true); refreshQueue(); };
    const handleOffline = () => setIsOnline(false);
    const handleQueueUpdate = () => refreshQueue();

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    window.addEventListener('offline-queue-updated', handleQueueUpdate);
    window.addEventListener('offline-op-synced', handleQueueUpdate);

    // Install auto-sync on reconnect
    const uninstall = installAutoSync(baseUrl);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
      window.removeEventListener('offline-queue-updated', handleQueueUpdate);
      window.removeEventListener('offline-op-synced', handleQueueUpdate);
      uninstall();
    };
  }, [baseUrl, refreshQueue]);

  // Don't render on server (SSR)
  if (!mounted) return null;

  const pendingCount = operations.filter((op) => op.status === 'PENDING' || op.status === 'SYNCING').length;
  const failedCount = operations.filter((op) => op.status === 'FAILED').length;

  // Rien a signaler = rien affiche : la puce verte « En ligne » permanente
  // contredisait les autres badges et volait de la place sur mobile. La
  // pastille n'apparait que pour une information reelle (hors ligne, ops en
  // attente de synchro, erreur de synchro).
  if (isOnline && pendingCount === 0 && failedCount === 0 && !showPanel) {
    return null;
  }

  const handleManualSync = async () => {
    if (!isOnline || isSyncing) return;
    setIsSyncing(true);
    try {
      await syncOutbox(baseUrl);
      await refreshQueue();
    } finally {
      setIsSyncing(false);
    }
  };

  const getStatusColor = () => {
    if (!isOnline) return '#ef4444'; // red
    if (failedCount > 0) return '#f97316'; // orange
    if (pendingCount > 0) return '#eab308'; // yellow
    return '#22c55e'; // green
  };

  const getStatusText = () => {
    if (!isOnline) {
      return pendingCount > 0
        ? `Hors ligne  ${pendingCount} en file`
        : 'Hors ligne';
    }
    if (isSyncing) return 'Synchronisation…';
    if (failedCount > 0) return `${failedCount} erreur(s)`;
    if (pendingCount > 0) return `${pendingCount} en attente`;
    return 'En ligne';
  };

  const getTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      TICKET_CARBURANT: '⛽ Ticket carburant',
      EPOD_SIGNATURE: '✍️ ePOD Signature',
      QHSE_INCIDENT: '⚠️ Incident QHSE',
      PANNE_VEHICULE: '🔧 Panne véhicule',
      POINTAGE_CHAUFFEUR: '📍 Pointage',
      GENERIC_POST: '📤 Envoi',
    };
    return labels[type] || type;
  };

  const getStatusBadge = (status: string) => {
    const badges: Record<string, { text: string; color: string }> = {
      PENDING: { text: 'En attente', color: '#eab308' },
      SYNCING: { text: 'Sync…', color: '#3b82f6' },
      SYNCED: { text: 'Synchronisé', color: '#22c55e' },
      FAILED: { text: 'Échec', color: '#ef4444' },
    };
    return badges[status] || { text: status, color: '#6b7280' };
  };

  const dotColor = getStatusColor();

  return (
    <div style={{ position: 'relative', display: 'inline-block' }}>
      {/* Indicator button */}
      <button
        onClick={() => setShowPanel(!showPanel)}
        title={getStatusText()}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          padding: '4px 10px',
          borderRadius: '20px',
          border: `1px solid ${dotColor}30`,
          background: `${dotColor}15`,
          cursor: 'pointer',
          fontSize: '12px',
          fontWeight: 500,
          color: dotColor,
          transition: 'all 0.2s ease',
        }}
      >
        {/* Animated dot */}
        <span
          style={{
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            background: dotColor,
            flexShrink: 0,
            animation: (!isOnline || pendingCount > 0)
              ? 'offline-pulse 1.5s ease-in-out infinite'
              : 'none',
          }}
        />
        <span>{getStatusText()}</span>
        {/* Badge for pending count */}
        {pendingCount > 0 && (
          <span
            style={{
              background: dotColor,
              color: '#fff',
              borderRadius: '10px',
              padding: '0 6px',
              fontSize: '10px',
              fontWeight: 700,
              lineHeight: '16px',
            }}
          >
            {pendingCount}
          </span>
        )}
      </button>

      {/* Dropdown panel */}
      {showPanel && (
        <div
          style={{
            position: 'absolute',
            top: 'calc(100% + 8px)',
            right: 0,
            width: '320px',
            background: 'var(--card, #1e2433)',
            border: '1px solid rgba(255,255,255,0.1)',
            borderRadius: '12px',
            boxShadow: '0 20px 40px rgba(0,0,0,0.4)',
            zIndex: 9999,
            overflow: 'hidden',
          }}
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div
            style={{
              padding: '12px 16px',
              borderBottom: '1px solid rgba(255,255,255,0.08)',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
            }}
          >
            <span style={{ fontWeight: 600, fontSize: '14px', color: '#e2e8f0' }}>
              📡 File d'attente hors ligne
            </span>
            {isOnline && pendingCount > 0 && (
              <button
                onClick={handleManualSync}
                disabled={isSyncing}
                style={{
                  padding: '4px 12px',
                  borderRadius: '8px',
                  background: '#3b82f6',
                  color: '#fff',
                  border: 'none',
                  fontSize: '12px',
                  cursor: isSyncing ? 'not-allowed' : 'pointer',
                  opacity: isSyncing ? 0.6 : 1,
                }}
              >
                {isSyncing ? '⏳ Sync…' : '🔄 Synchroniser'}
              </button>
            )}
          </div>

          {/* Operations list */}
          <div style={{ maxHeight: '300px', overflowY: 'auto' }}>
            {operations.length === 0 ? (
              <div
                style={{
                  padding: '24px',
                  textAlign: 'center',
                  color: '#64748b',
                  fontSize: '13px',
                }}
              >
                ✅ Aucune opération en attente
              </div>
            ) : (
              operations.map((op) => {
                const badge = getStatusBadge(op.status);
                return (
                  <div
                    key={op.id}
                    style={{
                      padding: '10px 16px',
                      borderBottom: '1px solid rgba(255,255,255,0.05)',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'flex-start',
                      gap: '8px',
                    }}
                  >
                    <div>
                      <div style={{ fontSize: '13px', color: '#e2e8f0', fontWeight: 500 }}>
                        {getTypeLabel(op.type)}
                      </div>
                      <div style={{ fontSize: '11px', color: '#64748b', marginTop: '2px' }}>
                        {new Date(op.created_at).toLocaleString('fr-FR', {
                          day: '2-digit',
                          month: '2-digit',
                          hour: '2-digit',
                          minute: '2-digit',
                        })}
                        {op.attempt_count > 0 && ` · ${op.attempt_count} tentative(s)`}
                      </div>
                      {op.error && (
                        <div style={{ fontSize: '11px', color: '#ef4444', marginTop: '2px' }}>
                          {op.error.slice(0, 60)}…
                        </div>
                      )}
                    </div>
                    <span
                      style={{
                        padding: '2px 8px',
                        borderRadius: '10px',
                        background: `${badge.color}20`,
                        color: badge.color,
                        fontSize: '11px',
                        fontWeight: 600,
                        whiteSpace: 'nowrap',
                        flexShrink: 0,
                      }}
                    >
                      {badge.text}
                    </span>
                  </div>
                );
              })
            )}
          </div>

          {/* Footer */}
          <div
            style={{
              padding: '8px 16px',
              borderTop: '1px solid rgba(255,255,255,0.08)',
              fontSize: '11px',
              color: '#475569',
              textAlign: 'center',
            }}
          >
            {operations.length} opération(s) total · Données stockées localement
          </div>
        </div>
      )}

      {/* Click outside to close */}
      {showPanel && (
        <div
          style={{ position: 'fixed', inset: 0, zIndex: 9998 }}
          onClick={() => setShowPanel(false)}
        />
      )}

      {/* Pulse animation */}
      <style>{`
        @keyframes offline-pulse {
          0%, 100% { opacity: 1; transform: scale(1); }
          50% { opacity: 0.5; transform: scale(1.3); }
        }
      `}</style>
    </div>
  );
}
