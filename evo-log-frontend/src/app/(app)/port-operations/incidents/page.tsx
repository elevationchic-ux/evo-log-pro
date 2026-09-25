'use client';

import React, { useCallback, useEffect, useState } from 'react';
import { toast } from 'sonner';
import Link from 'next/link';
import {
  AlertTriangle, Plus, Search, ArrowLeft, RefreshCw,
  FileText, ShieldAlert
} from 'lucide-react';
import api from '@/lib/api';
import { useSettings } from '@/components/layout/SettingsProvider';

interface PortIncident {
  id: number;
  type: string;
  numero: string;
  date: string | null;
  lieu: string | null;
  type_accident?: string | null;
  gravite: string | null;
  statut: string | null;
  montant_dommages?: number | null;
  blesses?: number | null;
  deces?: number | null;
  arret_travail?: boolean | null;
}

const GRAVITE_STYLE: Record<string, string> = {
  grave: 'bg-red-500/20 text-red-400',
  mortel: 'bg-red-500/30 text-red-300',
  moyenne: 'bg-amber-500/20 text-amber-400',
  legere: 'bg-blue-500/20 text-blue-400',
  leger: 'bg-blue-500/20 text-blue-400',
};

function fmtDate(v: string | null): string {
  if (!v) return '';
  const d = new Date(v);
  return Number.isNaN(d.getTime()) ? v : d.toLocaleDateString('fr-FR');
}

// Échappement HTML : les champs proviennent du backend / de saisie terrain et sont
// injectés dans le document d'impression via document.write.
function esc(v: unknown): string {
  return String(v ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

export default function PortOperationsIncidentsPage() {
  const { language } = useSettings();
  const lang = language === 'en' ? 'en' : 'fr';
  const t = (fr: string, en: string) => (lang === 'en' ? en : fr);

  const [incidents, setIncidents] = useState<PortIncident[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(false);
  const [loaded, setLoaded] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [saving, setSaving] = useState(false);

  const [formData, setFormData] = useState({
    type_accident: 'Avarie de Conteneur (Choc / Déformation)',
    lieu: '',
    date: '',
    gravite: 'moyenne',
    description: '',
  });

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await api.get('/api/v1/port-incidents/', { params: { limit: 100 } });
      const data = res.data ?? {};
      const rows: PortIncident[] = [
        ...(data.incidents_transport ?? []),
        ...(data.incidents_travail ?? []),
      ];
      setIncidents(rows);
      setLoaded(true);
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || t('Erreur de chargement', 'Failed to load'));
    } finally {
      setLoading(false);
    }
  }, [lang]);

  useEffect(() => {
    load();
  }, [load]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      await api.post('/api/v1/port-incidents/', {
        type_accident: formData.type_accident,
        lieu: formData.lieu || 'Port',
        date: formData.date || undefined,
        gravite: formData.gravite,
        description: formData.description,
      });
      toast.success(t('Incident déclaré et enregistré.', 'Incident recorded.'));
      setIsModalOpen(false);
      setFormData({ type_accident: 'Avarie de Conteneur (Choc / Déformation)', lieu: '', date: '', gravite: 'moyenne', description: '' });
      await load();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || t("Échec de la déclaration de l'incident.", 'Failed to record incident.'));
    } finally {
      setSaving(false);
    }
  };

  // Impression réelle du constat : document construit depuis la ligne affichée, via la boîte d'impression du navigateur.
  const handlePrintConstat = (i: PortIncident) => {
    const win = window.open('', '_blank', 'width=800,height=600');
    if (!win) {
      toast.error(t("Impression impossible : la fenêtre d'impression a été bloquée par le navigateur.", 'Print blocked by the browser.'));
      return;
    }
    win.document.write(`<!DOCTYPE html><html lang="fr"><head><title>Constat ${esc(i.numero)}</title></head>
      <body style="font-family:Arial,sans-serif;padding:32px;color:#0f172a">
        <h1>Constat d'Incident Portuaire</h1>
        <p><strong>Numéro :</strong> ${esc(i.numero)}</p>
        <p><strong>Nature :</strong> ${esc(i.type_accident || i.type)}</p>
        <p><strong>Lieu :</strong> ${esc(i.lieu || '')}</p>
        <p><strong>Date :</strong> ${esc(fmtDate(i.date))}</p>
        <p><strong>Gravité :</strong> ${esc(i.gravite || '')}  <strong>Statut :</strong> ${esc(i.statut || '')}</p>
        ${i.montant_dommages != null ? `<p><strong>Dommage estimé :</strong> ${esc(i.montant_dommages.toLocaleString())} XAF</p>` : ''}
        <p style="margin-top:48px">Signature manutentionnaire : ______________________ &nbsp;&nbsp;&nbsp; Signature accaisseur : ______________________</p>
        <script>window.print()</script>
      </body></html>`);
    win.document.close();
  };

  const filtered = incidents.filter(i => {
    const q = search.toLowerCase();
    return !q
      || (i.numero || '').toLowerCase().includes(q)
      || (i.type_accident || '').toLowerCase().includes(q)
      || (i.lieu || '').toLowerCase().includes(q);
  });

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-4 sm:p-6 pb-24 text-slate-100">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-xs text-slate-400">
        <Link href="/port-operations" className="hover:text-blue-400 flex items-center gap-1">
          <ArrowLeft className="w-3.5 h-3.5" /> {t('Opérations Portuaires', 'Port Operations')}
        </Link>
        <span>/</span>
        <span className="text-white">{t('Avaries Quai & Incidents de Manutention', 'Dock Damage & Handling Incidents')}</span>
      </div>

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 bg-slate-900/80 p-6 rounded-2xl border border-slate-800 backdrop-blur-xl">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-red-500/10 text-red-400 rounded-xl border border-red-500/20">
            <AlertTriangle className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
              {t('Avaries Quai & Incidents de Manutention', 'Dock Damage & Handling Incidents')}
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-red-500/10 text-red-400 border border-red-500/30 font-mono">
                KACC_INC
              </span>
            </h1>
            <p className="text-sm text-slate-400">
              {t('Déclaration des constats d\'incident, réserves contradictoires et dossiers assurances', 'Incident reports, contradictory reservations and insurance files')}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={load}
            disabled={loading}
            className="flex items-center gap-2 px-4 py-2 rounded-xl border border-slate-700 bg-slate-800 hover:bg-slate-700 text-white font-medium text-sm disabled:opacity-50 transition"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            {t('Actualiser', 'Refresh')}
          </button>
          <button
            onClick={() => setIsModalOpen(true)}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-red-600 hover:bg-red-500 text-white font-medium text-sm shadow-lg shadow-red-600/30 transition"
          >
            <Plus className="w-4 h-4" />
            {t('Déclarer un Incident', 'Report an Incident')}
          </button>
        </div>
      </div>

      {/* Main Table card */}
      <div className="bg-slate-900/80 rounded-2xl border border-slate-800 p-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
          <div className="relative flex-1 max-w-md">
            <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
            <input
              type="text"
              value={search}
              onChange={e => setSearch(e.target.value)}
              placeholder={t("Rechercher numéro, nature, lieu...", "Search number, type, location...")}
              className="w-full pl-9 pr-4 py-2 text-sm bg-slate-800/90 border border-slate-700 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:border-red-500"
            />
          </div>
        </div>

        {filtered.length === 0 ? (
          <div className="py-16 text-center bg-slate-950/40 rounded-xl border border-dashed border-slate-800">
            <ShieldAlert className="w-12 h-12 text-slate-400 mx-auto mb-3" />
            <h3 className="text-base font-semibold text-white">
              {loaded ? t('Aucun incident enregistré', 'No incident recorded') : t('Chargement…', 'Loading…')}
            </h3>
            {loaded && (
              <>
                <p className="text-sm text-slate-400 max-w-md mx-auto mt-1 mb-4">
                  {t('La zone de manutention ne recense aucun incident en cours.', 'The handling area lists no ongoing incident.')}
                </p>
                <button
                  onClick={() => setIsModalOpen(true)}
                  className="inline-flex items-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-500 text-white text-sm font-medium rounded-xl shadow transition"
                >
                  <Plus className="w-4 h-4" />
                  {t("Déclarer un constat d'incident", 'Report an incident')}
                </button>
              </>
            )}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="bg-slate-800/60 text-slate-400 text-xs uppercase font-medium">
                <tr>
                  <th className="py-3 px-4 rounded-l-xl">{t('N° Dossier', 'File No.')}</th>
                  <th className="py-3 px-4">{t('Nature', 'Type')}</th>
                  <th className="py-3 px-4">{t('Date', 'Date')}</th>
                  <th className="py-3 px-4">{t('Lieu', 'Location')}</th>
                  <th className="py-3 px-4">{t('Dommage (XAF)', 'Damage (XAF)')}</th>
                  <th className="py-3 px-4">{t('Gravité', 'Severity')}</th>
                  <th className="py-3 px-4">{t('Statut', 'Status')}</th>
                  <th className="py-3 px-4 rounded-r-xl text-right">{t('Action', 'Action')}</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {filtered.map(i => (
                  <tr key={`${i.type}-${i.id}`} className="hover:bg-slate-800/40 transition">
                    <td className="py-3.5 px-4 font-mono font-medium text-red-400">{i.numero}</td>
                    <td className="py-3.5 px-4 text-xs text-slate-300">{i.type_accident || i.type}</td>
                    <td className="py-3.5 px-4 text-xs text-slate-400">{fmtDate(i.date)}</td>
                    <td className="py-3.5 px-4 text-xs text-white">{i.lieu || ''}</td>
                    <td className="py-3.5 px-4 font-mono text-xs text-white font-bold">
                      {i.montant_dommages != null ? `${i.montant_dommages.toLocaleString()} XAF` : ''}
                    </td>
                    <td className="py-3.5 px-4">
                      <span className={`px-2 py-0.5 rounded text-xs font-semibold ${GRAVITE_STYLE[(i.gravite || '').toLowerCase()] || 'bg-slate-500/20 text-slate-400'}`}>
                        {i.gravite || ''}
                      </span>
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20">
                        {i.statut || ''}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <button
                        onClick={() => handlePrintConstat(i)}
                        className="p-1.5 hover:bg-slate-800 rounded text-slate-400 hover:text-white transition"
                        title={t("Télécharger le constat", 'Download report')}
                      >
                        <FileText className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Modal Déclaration */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-lg w-full p-6 shadow-2xl">
            <h3 className="text-lg font-bold text-white mb-1 flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-red-400" />
              {t('Émettre un Constat d\'Incident', 'Issue an Incident Report')}
            </h3>
            <p className="text-xs text-slate-400 mb-4">
              {t('Constat officiel enregistré dans la base des incidents portuaires.', 'Official report recorded in the port incidents database.')}
            </p>

            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-xs text-slate-300 mb-1">{t('Nature de l\'incident', 'Incident type')}</label>
                <select
                  value={formData.type_accident}
                  onChange={e => setFormData({ ...formData, type_accident: e.target.value })}
                  className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-red-500"
                >
                  <option value="Avarie de Conteneur (Choc / Déformation)">{t('Choc / Déformation Paroi', 'Wall impact / deformation')}</option>
                  <option value="Perforation Toit / Plancher">{t('Perforation Toit / Plancher', 'Roof / floor perforation')}</option>
                  <option value="Rupture de Scellé Douane / Ligne">{t('Rupture de Scellé', 'Seal break')}</option>
                  <option value="Panne Groupe Frigorifique (Reefer)">{t('Panne Groupe Reefer', 'Reefer failure')}</option>
                  <option value="Chute de Charge Manutention">{t('Chute de Charge', 'Dropped load')}</option>
                </select>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-slate-300 mb-1">{t('Degré de Gravité', 'Severity')}</label>
                  <select
                    value={formData.gravite}
                    onChange={e => setFormData({ ...formData, gravite: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-red-500"
                  >
                    <option value="legere">{t('Légère (Cosmétique)', 'Light (cosmetic)')}</option>
                    <option value="moyenne">{t('Moyenne (Réparation requise)', 'Medium (repair required)')}</option>
                    <option value="grave">{t('Grave', 'Severe')}</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs text-slate-300 mb-1">{t('Date de l\'incident', 'Incident date')}</label>
                  <input
                    type="date"
                    value={formData.date}
                    onChange={e => setFormData({ ...formData, date: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-red-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs text-slate-300 mb-1">{t('Lieu sur le Port', 'Location on port')}</label>
                <input
                  type="text"
                  value={formData.lieu}
                  onChange={e => setFormData({ ...formData, lieu: e.target.value })}
                  placeholder={t('Ex: Quai 5, Terminal à conteneurs', 'e.g. Dock 5, Container Terminal')}
                  className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-red-500"
                />
              </div>

              <div>
                <label className="block text-xs text-slate-300 mb-1">{t('Description des Circonstances', 'Circumstances')}</label>
                <textarea
                  rows={2}
                  value={formData.description}
                  onChange={e => setFormData({ ...formData, description: e.target.value })}
                  className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-red-500"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 text-sm text-slate-400 hover:text-white"
                >
                  {t('Annuler', 'Cancel')}
                </button>
                <button
                  type="submit"
                  disabled={saving}
                  className="px-5 py-2 bg-red-600 hover:bg-red-500 disabled:opacity-50 text-white text-sm font-medium rounded-xl shadow-lg transition"
                >
                  {saving ? t('Enregistrement…', 'Saving…') : t('Enregistrer le constat', 'Save report')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
