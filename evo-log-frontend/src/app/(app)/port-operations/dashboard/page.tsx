'use client';

import { useState } from 'react';

export default function PortOperationsDashboardPage() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-on-surface">🚢 Control Tower Maritime</h1>
          <p className="text-on-surface-variant">Centre de contrôle temps réel des opérations portuaires</p>
        </div>
        <div className="flex gap-3">
          <button className="rounded-lg border border-outline bg-surface px-4 py-2 text-sm font-medium text-on-surface hover:bg-surface-container">
            Actualiser
          </button>
          <button className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-on-primary hover:opacity-90">
            Nouveau Manifeste
          </button>
        </div>
      </div>

      {/* KPIs Cards */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <div className="erp-card p-6">
          <div className="flex items-center gap-4">
            <div className="rounded-lg bg-blue-500/10 p-3">
              <span className="material-symbols-outlined text-blue-600">anchor</span>
            </div>
            <div>
              <p className="text-2xl font-bold text-on-surface">12</p>
              <p className="text-sm text-on-surface-variant">Navires à Quai</p>
            </div>
          </div>
        </div>

        <div className="erp-card p-6">
          <div className="flex items-center gap-4">
            <div className="rounded-lg bg-amber-500/10 p-3">
              <span className="material-symbols-outlined text-amber-600">schedule</span>
            </div>
            <div>
              <p className="text-2xl font-bold text-on-surface">8</p>
              <p className="text-sm text-on-surface-variant">En Attente</p>
            </div>
          </div>
        </div>

        <div className="erp-card p-6">
          <div className="flex items-center gap-4">
            <div className="rounded-lg bg-emerald-500/10 p-3">
              <span className="material-symbols-outlined text-emerald-600">local_shipping</span>
            </div>
            <div>
              <p className="text-2xl font-bold text-on-surface">2,847</p>
              <p className="text-sm text-on-surface-variant">TEU Déchargés</p>
            </div>
          </div>
        </div>

        <div className="erp-card p-6">
          <div className="flex items-center gap-4">
            <div className="rounded-lg bg-red-500/10 p-3">
              <span className="material-symbols-outlined text-red-600">warning</span>
            </div>
            <div>
              <p className="text-2xl font-bold text-on-surface">3</p>
              <p className="text-sm text-on-surface-variant">Alertes Critiques</p>
            </div>
          </div>
        </div>
      </div>

      {/* Live Operations */}
      <div className="grid gap-6 lg:grid-cols-2">
        <div className="erp-card">
          <div className="erp-card-header">
            <h3 className="font-semibold text-on-surface">Escales en Cours</h3>
          </div>
          <div className="erp-card-body">
            <div className="space-y-4">
              <div className="flex items-center justify-between rounded-lg border border-outline p-4">
                <div>
                  <p className="font-medium text-on-surface">MSC LORENA</p>
                  <p className="text-sm text-on-surface-variant">Poste 4 • Déchargement</p>
                </div>
                <span className="status-badge status-loading">EN COURS</span>
              </div>
              <div className="flex items-center justify-between rounded-lg border border-outline p-4">
                <div>
                  <p className="font-medium text-on-surface">CMA CGM BOUGAINVILLE</p>
                  <p className="text-sm text-on-surface-variant">Poste 7 • Chargement</p>
                </div>
                <span className="status-badge status-transit">CHARGEMENT</span>
              </div>
            </div>
          </div>
        </div>

        <div className="erp-card">
          <div className="erp-card-header">
            <h3 className="font-semibold text-on-surface">Manifestes du Jour</h3>
          </div>
          <div className="erp-card-body">
            <div className="space-y-4">
              <div className="flex items-center justify-between rounded-lg border border-outline p-4">
                <div>
                  <p className="font-medium text-on-surface">MAN-DLA-2024-0847</p>
                  <p className="text-sm text-on-surface-variant">342 conteneurs • MSC LORENA</p>
                </div>
                <span className="status-badge status-delivered">VALIDÉ</span>
              </div>
              <div className="flex items-center justify-between rounded-lg border border-outline p-4">
                <div>
                  <p className="font-medium text-on-surface">MAN-DLA-2024-0848</p>
                  <p className="text-sm text-on-surface-variant">127 conteneurs • En attente</p>
                </div>
                <span className="status-badge status-planified">EN ATTENTE</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}