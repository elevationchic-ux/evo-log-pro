'use client';

export default function DossiersCemacPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-on-surface">🌍 Dossiers Transit CEMAC</h1>
          <p className="text-on-surface-variant">Gestion dossiers transit zone CEMAC, TEC, TVA</p>
        </div>
      </div>
      <div className="erp-card">
        <div className="erp-card-body">
          <p className="text-center text-on-surface-variant py-8">
            Module en cours de développement - Dossiers Transit CEMAC 🇨🇲
            <br />
            <span className="text-sm">Fonctionnalités: TEC CEMAC, transit régional, procédures douanières</span>
          </p>
        </div>
      </div>
    </div>
  );
}