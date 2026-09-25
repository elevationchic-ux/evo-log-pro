'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  KPICard, Card, CardHeader, CardContent, DataTable, StatusBadge, PageHeader,
} from '@/components/ui';
import { apiClient } from '@/lib/api-client';
import { useSettings } from '@/components/layout/SettingsProvider';
import { toast } from 'sonner';

interface Vehicle {
  id: number;
  immatriculation: string;
  type: string;
  brand: string;
  model: string;
  year: string | number;
  status: string;
  mileage: number | string;
  prochaine_maintenance?: string | null;
}

const emptyForm = {
  immatriculation: '', marque: '', modele: '', annee: '', capacite_tonnage: '', kilometrage: '', status: 'ACTIVE',
};

export default function TransportFlottePage() {
  const { language } = useSettings();
  const lang = language === 'en' ? 'en' : 'fr';
  const t = (fr: string, en: string) => (lang === 'en' ? en : fr);

  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [kpis, setKpis] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [form, setForm] = useState(emptyForm);
  const [saving, setSaving] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [v, k] = await Promise.all([
        apiClient.get('/api/v1/transport/camions', { params: { limit: 200 } }),
        apiClient.get('/api/v1/transport/kpis').catch(() => null),
      ]);
      const rows = Array.isArray(v.data) ? v.data : (v.data?.items ?? []);
      setVehicles(rows.map((c: any) => ({
        id: c.id,
        immatriculation: c.immatriculation,
        type: c.type_vehicule || c.categorie || '',
        brand: c.marque || '',
        model: c.modele || '',
        year: c.annee ?? '',
        status: String(c.status || ''),
        mileage: Number(c.kilometrage ?? 0),
        prochaine_maintenance: c.prochaine_maintenance,
      })));
      setKpis(k?.data ?? null);
    } catch {
      toast.error(t(
        "Le parc véhicule n'a pas pu être chargé. Vérifiez votre connexion.",
        'Vehicle fleet could not be loaded. Check your connection.'
      ));
    } finally {
      setLoading(false);
    }
  }, [lang]);

  useEffect(() => { load(); }, [load]);

  const submit = async () => {
    if (!form.immatriculation.trim()) {
      toast.error(t('Immatriculation requise.', 'Registration number required.'));
      return;
    }
    setSaving(true);
    try {
      await apiClient.post('/api/v1/transport/camions', {
        immatriculation: form.immatriculation.trim(),
        marque: form.marque || undefined,
        modele: form.modele || undefined,
        annee: form.annee ? Number(form.annee) : undefined,
        capacite_tonnage: form.capacite_tonnage ? Number(form.capacite_tonnage) : undefined,
        kilometrage: form.kilometrage ? Number(form.kilometrage) : undefined,
        status: form.status,
      });
      toast.success(t('Véhicule enregistré.', 'Vehicle registered.'));
      setModalOpen(false);
      setForm(emptyForm);
      load();
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || t('Échec de lenregistrement.', 'Registration failed.'));
    } finally {
      setSaving(false);
    }
  };

  const exporter = () => {
    if (vehicles.length === 0) {
      toast.info(t('Aucun véhicule à exporter.', 'No vehicle to export.'));
      return;
    }
    const header = ['Immatriculation', 'Marque', 'Modele', 'Annee', 'Statut', 'Kilometrage'];
    const lines = vehicles.map((v) =>
      [v.immatriculation, v.brand, v.model, v.year, v.status, v.mileage].map((x) => `"${String(x).replace(/"/g, '""')}"`).join(',')
    );
    const csv = [header.join(','), ...lines].join('\n');
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'flotte_vehicules.csv';
    a.click();
    URL.revokeObjectURL(url);
  };

  const statusVariant = (s: string) =>
    s === 'ACTIVE' ? 'success' : s === 'IN_MAINTENANCE' ? 'warning' : s === 'IMMOBILISE' || s === 'OUT_OF_SERVICE' ? 'error' : 'default';

  const columns = [
    { key: 'immatriculation', header: t('Immatriculation', 'Registration'), sortable: true },
    { key: 'brand', header: t('Marque', 'Brand') },
    { key: 'model', header: t('Modèle', 'Model') },
    { key: 'year', header: t('Année', 'Year'), sortable: true },
    { key: 'status', header: t('Statut', 'Status'), render: (item: any) => <StatusBadge label={String(item.status)} variant={statusVariant(item.status) as any} /> },
    { key: 'mileage', header: t('Kilométrage', 'Mileage'), sortable: true },
  ];

  // Répartition par statut, calculée sur le parc réellement chargé.
  const statusCounts = vehicles.reduce<Record<string, number>>((acc, v) => {
    acc[v.status] = (acc[v.status] || 0) + 1;
    return acc;
  }, {});
  const revisions = vehicles.filter((v) => v.prochaine_maintenance).slice(0, 6);

  return (
    <div className="space-y-6">
      <PageHeader
        title="🚚 Gestion de la Flotte"
        description={t(
          'Camions, tracteurs, remorques - Suivi complet du parc véhicule',
          'Trucks, tractors, trailers - Full fleet tracking'
        )}
        breadcrumbs={[{ label: 'Transport', href: '/transport' }, { label: t('Flotte', 'Fleet') }]}
        actions={
          <button onClick={() => setModalOpen(true)} className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-on-primary hover:opacity-90 flex items-center gap-2">
            <span className="material-symbols-outlined text-[18px]">add</span>
            {t('Ajouter Véhicule', 'Add Vehicle')}
          </button>
        }
      />

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <KPICard title={t('Parc Total', 'Total Fleet')} value={kpis?.vehicules_total ?? '0'} subtitle={t('Camions enregistrés', 'Registered trucks')} icon={<span className="material-symbols-outlined text-2xl">directions_car</span>} color="blue" loading={loading} />
        <KPICard title={t('En Service', 'In Service')} value={kpis?.vehicules_actifs ?? '0'} subtitle={t('Statut actif', 'Active status')} icon={<span className="material-symbols-outlined text-2xl">check_circle</span>} color="emerald" loading={loading} />
        <KPICard title={t('En Maintenance', 'In Maintenance')} value={kpis?.camions_en_maintenance ?? '0'} subtitle={t('Atelier GMAO', 'Workshop')} icon={<span className="material-symbols-outlined text-2xl">build</span>} color="amber" loading={loading} />
        <KPICard title={t('TauxDisponibilité', 'Availability')} value={kpis ? `${kpis.taux_disponibilite}%` : '0%'} subtitle={t('Flotte opérationnelle', 'Operational fleet')} icon={<span className="material-symbols-outlined text-2xl">speed</span>} color="blue" loading={loading} />
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <Card>
            <CardHeader
              title={t('Inventaire Flotte', 'Fleet Inventory')}
              subtitle={t('Tous véhicules enregistrés', 'All registered vehicles')}
              icon={<span className="material-symbols-outlined text-xl">inventory_2</span>}
              action={<button onClick={exporter} className="text-sm text-primary hover:underline">{t('Exporter', 'Export')}</button>}
            />
            <CardContent>
              <DataTable data={vehicles} columns={columns} keyField="id" loading={loading} />
            </CardContent>
          </Card>
        </div>

        <div className="space-y-6">
          <Card>
            <CardHeader title={t('Répartition par Statut', 'Status Breakdown')} icon={<span className="material-symbols-outlined text-xl">pie_chart</span>} />
            <CardContent>
              {Object.keys(statusCounts).length === 0 ? (
                <div className="rounded-lg bg-slate-500/10 p-3 text-sm text-slate-500">{t('Aucun véhicule enregistré.', 'No vehicle registered.')}</div>
              ) : (
                <div className="space-y-2">
                  {Object.entries(statusCounts).map(([s, n]) => (
                    <div key={s} className="flex items-center justify-between text-sm">
                      <StatusBadge label={s} variant={statusVariant(s) as any} />
                      <span className="font-mono text-slate-500">{n}</span>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader title={t('Prochaines Révisions', 'Upcoming Maintenance')} icon={<span className="material-symbols-outlined text-xl">event</span>} />
            <CardContent>
              {revisions.length === 0 ? (
                <div className="rounded border border-slate-700 bg-slate-500/5 p-3 text-sm text-slate-500">{t('Aucune révision planifiée.', 'No scheduled maintenance.')}</div>
              ) : (
                <div className="space-y-2">
                  {revisions.map((v) => (
                    <div key={v.id} className="flex items-center justify-between text-xs">
                      <span className="font-mono text-slate-300">{v.immatriculation}</span>
                      <span className="text-amber-400">{new Date(v.prochaine_maintenance!).toLocaleDateString(lang === 'en' ? 'en-GB' : 'fr-FR')}</span>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {modalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4" onClick={() => setModalOpen(false)}>
          <div className="w-full max-w-lg rounded-2xl border border-slate-700 bg-slate-900 p-6 shadow-xl" onClick={(e) => e.stopPropagation()}>
            <h3 className="mb-4 text-lg font-bold text-slate-100">{t('Ajouter un véhicule', 'Add a vehicle')}</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <label className="text-xs text-slate-400">{t('Immatriculation *', 'Registration *')}
                <input value={form.immatriculation} onChange={(e) => setForm({ ...form, immatriculation: e.target.value })} className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100" />
              </label>
              <label className="text-xs text-slate-400">{t('Statut', 'Status')}
                <select value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value })} className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100">
                  <option value="ACTIVE">{t('Actif', 'Active')}</option>
                  <option value="IN_MAINTENANCE">{t('Maintenance', 'Maintenance')}</option>
                  <option value="IMMOBILISE">{t('Immobilisé', 'Immobilized')}</option>
                </select>
              </label>
              <label className="text-xs text-slate-400">{t('Marque', 'Brand')}
                <input value={form.marque} onChange={(e) => setForm({ ...form, marque: e.target.value })} className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100" />
              </label>
              <label className="text-xs text-slate-400">{t('Modèle', 'Model')}
                <input value={form.modele} onChange={(e) => setForm({ ...form, modele: e.target.value })} className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100" />
              </label>
              <label className="text-xs text-slate-400">{t('Année', 'Year')}
                <input type="number" inputMode="numeric" value={form.annee} onChange={(e) => setForm({ ...form, annee: e.target.value })} className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100" />
              </label>
              <label className="text-xs text-slate-400">{t('Capacité (t)', 'Capacity (t)')}
                <input type="number" inputMode="decimal" value={form.capacite_tonnage} onChange={(e) => setForm({ ...form, capacite_tonnage: e.target.value })} className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100" />
              </label>
              <label className="text-xs text-slate-400 sm:col-span-2">{t('Kilométrage', 'Mileage')}
                <input type="number" inputMode="numeric" value={form.kilometrage} onChange={(e) => setForm({ ...form, kilometrage: e.target.value })} className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100" />
              </label>
            </div>
            <div className="mt-5 flex justify-end gap-2">
              <button onClick={() => setModalOpen(false)} className="rounded-lg border border-slate-700 px-4 py-2 text-sm text-slate-300 hover:bg-slate-800">{t('Annuler', 'Cancel')}</button>
              <button onClick={submit} disabled={saving} className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-on-primary hover:opacity-90 disabled:opacity-60">{saving ? t('Enregistrement…', 'Saving…') : t('Enregistrer', 'Save')}</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
