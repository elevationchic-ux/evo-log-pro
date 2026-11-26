'use client';

import React, { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import {
  KPICard, Card, CardHeader, CardContent, DataTable, StatusBadge, StatusBadges, PageHeader,
} from '@/components/ui';
import { magasinAPI, receptionMag3API } from '@/lib/api-client';
import { useSettings } from '@/components/layout/SettingsProvider';

interface ReceptionRow {
  id: number;
  numero_bon: string;
  zone: string;
  colis: number;
  statut: string;
  date: string;
}

interface OccupationZone {
  zone: string;
  nb_articles: number;
  valeur_stockee: number;
  occupancy: number | null;
}

export default function MagasinDashboardPage() {
  const { language } = useSettings();
  const lang = language === 'en' ? 'en' : 'fr';
  const t = (fr: string, en: string) => (lang === 'en' ? en : fr);

  const [kpis, setKpis] = useState<any>(null);
  const [loadingKpis, setLoadingKpis] = useState(true);
  const [receptions, setReceptions] = useState<ReceptionRow[]>([]);
  const [loadingRec, setLoadingRec] = useState(true);
  const [occupation, setOccupation] = useState<OccupationZone[]>([]);

  const load = useCallback(async () => {
    setLoadingKpis(true);
    setLoadingRec(true);
    try {
      const [k, r, o] = await Promise.all([
        magasinAPI.getKpis().catch(() => null),
        receptionMag3API.getAll({ limit: 20 }).catch(() => null),
        magasinAPI.getEntrepotsOccupation().catch(() => null),
      ]);
      setKpis(k?.data ?? null);
      const rows = r?.data?.items ?? [];
      setReceptions(
        rows.map((x: any) => ({
          id: x.id,
          numero_bon: x.numero_bon || ``,
          zone: x.entrepot_nom || '',
          colis: Number(x.nombre_lignes ?? 0),
          statut: x.statut || '',
          date: x.date_reception ? new Date(x.date_reception).toLocaleDateString(lang === 'en' ? 'en-GB' : 'fr-FR') : '',
        }))
      );
      const zones = o?.data?.zones ?? [];
      setOccupation(zones);
    } finally {
      setLoadingKpis(false);
      setLoadingRec(false);
    }
  }, [lang]);

  useEffect(() => {
    load();
  }, [load]);

  const columns = [
    { key: 'numero_bon', header: t('N° Réception', 'Receipt No.'), sortable: true },
    { key: 'zone', header: t('Entrepôt', 'Warehouse'), sortable: true },
    { key: 'colis', header: t('Lignes', 'Lines'), sortable: true },
    {
      key: 'statut',
      header: t('Statut', 'Status'),
      render: (item: any) =>
        (StatusBadges.Magasin as any)[item.statut] || <StatusBadge label={item.statut} />,
    },
    { key: 'date', header: t('Date', 'Date'), sortable: true },
  ];

  return (
    <div className="space-y-6">
      <PageHeader
        title="📦 K-Magasin WMS"
        description={t(
          "Gestion d'entrepôt, réception, stockage, préparation commandes",
          'Warehouse management, receiving, storage, order picking'
        )}
        breadcrumbs={[{ label: t('Magasin', 'Warehouse') }]}
        actions={
          <Link
            href="/magasin/mouvement-de-stock-manuel"
            className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-on-primary hover:opacity-90 flex items-center gap-2"
          >
            <span className="material-symbols-outlined text-[18px]">add</span>
            {t('Nouvelle Réception', 'New Receipt')}
          </Link>
        }
      />

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <KPICard
          title={t('Articles en Stock', 'Items in Stock')}
          value={kpis?.nb_articles ?? '0'}
          subtitle={t('Base stocks réelle', 'Live stock base')}
          icon={<span className="material-symbols-outlined text-2xl">inventory_2</span>}
          color="blue"
          loading={loadingKpis}
        />
        <KPICard
          title={t('Mouvements Jour', 'Movements Today')}
          value={kpis?.mouvements_jour ?? '0'}
          subtitle={t('Mouvements persistés', 'Persisted movements')}
          icon={<span className="material-symbols-outlined text-2xl">swap_horiz</span>}
          color="emerald"
          loading={loadingKpis}
        />
        <KPICard
          title={t('Valeur du Stock', 'Stock Value')}
          value={kpis ? `${Number(kpis.valeur_stock).toLocaleString(lang === 'en' ? 'en-US' : 'fr-FR')} FCFA` : '0'}
          subtitle={t('Valorisation WMS', 'WMS valuation')}
          icon={<span className="material-symbols-outlined text-2xl">payments</span>}
          color="violet"
          loading={loadingKpis}
        />
        <KPICard
          title={t('Alertes Stock', 'Stock Alerts')}
          value={kpis?.nb_alertes_min ?? '0'}
          subtitle={t('Sous seuil minimum', 'Below minimum')}
          icon={<span className="material-symbols-outlined text-2xl">warning</span>}
          color="amber"
          loading={loadingKpis}
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <Card>
            <CardHeader
              title={t('Réceptions récentes', 'Recent receipts')}
              subtitle={t('Historique des dernières réceptions', 'Latest receipt history')}
              icon={<span className="material-symbols-outlined text-xl">inbox</span>}
              action={
                <Link href="/magasin/stocks" className="text-sm text-primary hover:underline">
                  {t('Voir tout', 'View all')}
                </Link>
              }
            />
            <CardContent>
              <DataTable data={receptions} columns={columns} keyField="id" loading={loadingRec} />
              {!loadingRec && receptions.length === 0 && (
                <p className="mt-3 rounded-lg bg-slate-500/10 p-3 text-sm text-slate-500">
                  {t(
                    'Aucune réception enregistrée pour le moment.',
                    'No receipt recorded yet.'
                  )}
                </p>
              )}
            </CardContent>
          </Card>
        </div>

        <div className="space-y-6">
          <Card>
            <CardHeader
              title={t('Occupation Entrepôt', 'Warehouse Occupancy')}
              icon={<span className="material-symbols-outlined text-xl">warehouse</span>}
            />
            <CardContent>
              {occupation.length === 0 ? (
                <div className="rounded-lg bg-slate-500/10 p-3 text-sm text-slate-500">
                  {t('Aucun entrepôt enregistré.', 'No warehouse registered.')}
                </div>
              ) : (
                <div className="space-y-3">
                  {occupation.map((z, i) => (
                    <div key={i} className="flex items-center justify-between text-sm">
                      <span className="truncate text-slate-300 dark:text-slate-200">{z.zone}</span>
                      <span className="ml-2 shrink-0 font-mono text-xs text-slate-500">
                        {z.occupancy != null
                          ? `${z.occupancy}%`
                          : t(`${z.nb_articles} art.`, `${z.nb_articles} items`)}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader
              title={t('Alertes Importantes', 'Key Alerts')}
              icon={<span className="material-symbols-outlined text-xl text-red-500">notifications</span>}
            />
            <CardContent>
              <div className="rounded-lg bg-slate-500/10 p-3 text-sm text-slate-500">
                {kpis && kpis.nb_alertes_min > 0
                  ? t(
                    `${kpis.nb_alertes_min} article(s) sous le seuil minimum.`,
                    `${kpis.nb_alertes_min} item(s) below minimum threshold.`
                  )
                  : t('Aucune alerte de seuil actif.', 'No active threshold alerts.')}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
