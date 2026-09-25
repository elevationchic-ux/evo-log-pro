'use client';

import React, { useState } from 'react';
import { toast } from 'sonner';
import Link from 'next/link';
import {
  Scale, Plus, Search, ArrowLeft, CheckCircle2, Printer, AlertTriangle,
} from 'lucide-react';
import api from '@/lib/api';
import { useSettings } from '@/components/layout/SettingsProvider';
import { useAuth } from '@/components/shared/AuthProvider';

interface PeseeVGM {
  id: number;
  numero_ticket: string;
  numero_conteneur: string;
  type_conteneur: string;
  poids_brut: number;
  tare: number;
  masse_vgm: number;
  tolerance_conforme: boolean;
  camion_immatriculation: string;
  transporteur: string;
  date_pesee: string;
  operateur: string;
  certificat_solas: string;
}

// Échappement HTML : les champs proviennent de la saisie opérateur et sont injectés
// dans le document d'impression via document.write.
function esc(v: unknown): string {
  return String(v ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function makeTicketNumber(): string {
  const d = new Date();
  const pad = (n: number) => String(n).padStart(2, '0');
  return `PONT-${d.getFullYear()}${pad(d.getMonth() + 1)}${pad(d.getDate())}-${pad(d.getHours())}${pad(d.getMinutes())}${pad(d.getSeconds())}`;
}

export default function PortOperationsWeighbridgePage() {
  const { language } = useSettings();
  const lang = language === 'en' ? 'en' : 'fr';
  const t = (fr: string, en: string) => (lang === 'en' ? en : fr);
  const { user } = useAuth();

  const [pesees, setPesees] = useState<PeseeVGM[]>([]);
  const [search, setSearch] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [saving, setSaving] = useState(false);

  const [formData, setFormData] = useState({
    numero_conteneur: '',
    type_conteneur: "40' High Cube",
    poids_brut: 0,
    tare: 0,
    camion_immatriculation: '',
    transporteur: '',
  });

  const handleCreatePesee = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    const ticket = makeTicketNumber();
    try {
      // Calcul officiel du pont-bascule : masse nette VGM déterminée par le backend.
      const res = await api.post('/api/v1/sectoral/weighbridge', {
        ticket_number: ticket,
        vehicle_immat: formData.camion_immatriculation || formData.numero_conteneur,
        gross_weight_kg: formData.poids_brut,
        tare_weight_kg: formData.tare,
        commodity: formData.type_conteneur,
      });
      const data = res.data ?? {};
      const masseVgm: number = Number(data.net_weight_kg ?? Math.max(0, formData.poids_brut - formData.tare));
      const conforme: boolean = (data.variance_status ?? 'WITHIN_TOLERANCE') === 'WITHIN_TOLERANCE';
      const operateur: string =
        (user as any)?.fullName || (user as any)?.username || t('Opérateur pont-bascule', 'Weighbridge operator');

      const pesee: PeseeVGM = {
        id: Date.now(),
        numero_ticket: data.ticket_number || ticket,
        numero_conteneur: formData.numero_conteneur,
        type_conteneur: formData.type_conteneur,
        poids_brut: formData.poids_brut,
        tare: formData.tare,
        masse_vgm: masseVgm,
        tolerance_conforme: conforme,
        camion_immatriculation: formData.camion_immatriculation || '',
        transporteur: formData.transporteur || '',
        date_pesee: new Date().toLocaleString(lang === 'en' ? 'en-US' : 'fr-FR'),
        operateur,
        certificat_solas: `SOLAS-${ticket.slice(-10)}`,
      };
      setPesees(prev => [pesee, ...prev]);
      toast.success(t('Pesée calculée et certificat VGM généré.', 'Weighing computed and VGM certificate issued.'));
      setIsModalOpen(false);
      setFormData({
        numero_conteneur: '',
        type_conteneur: "40' High Cube",
        poids_brut: 0,
        tare: 0,
        camion_immatriculation: '',
        transporteur: '',
      });
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || t('Échec du calcul de la pesée.', 'Weighing calculation failed.'));
    } finally {
      setSaving(false);
    }
  };

  // Impression réelle du certificat VGM : document construit depuis la pesée affichée, via la boîte d'impression du navigateur.
  const handlePrintVgm = (p: PeseeVGM) => {
    const win = window.open('', '_blank', 'width=800,height=600');
    if (!win) {
      toast.error(t("Impression impossible : la fenêtre d'impression a été bloquée par le navigateur.", 'Print blocked by the browser.'));
      return;
    }
    win.document.write(`<!DOCTYPE html><html lang="fr"><head><title>Certificat VGM ${esc(p.numero_ticket)}</title></head>
      <body style="font-family:Arial,sans-serif;padding:32px;color:#0f172a">
        <h1>Certificat VGM  SOLAS VI/2</h1>
        <p><strong>N&deg; Ticket :</strong> ${esc(p.numero_ticket)}</p>
        <p><strong>Conteneur :</strong> ${esc(p.numero_conteneur)} (${esc(p.type_conteneur)})</p>
        <p><strong>Camion :</strong> ${esc(p.camion_immatriculation)}  ${esc(p.transporteur)}</p>
        <p><strong>Poids brut :</strong> ${esc(p.poids_brut.toLocaleString())} kg &nbsp;|&nbsp; <strong>Tare :</strong> ${esc(p.tare.toLocaleString())} kg</p>
        <h2>Masse V&eacute;rifi&eacute;e (VGM) : ${esc(p.masse_vgm.toLocaleString())} kg</h2>
        <p><strong>Conformit&eacute; tol&eacute;rance :</strong> ${p.tolerance_conforme ? 'CONFORME' : 'NON CONFORME'}</p>
        <p><strong>Date de pes&eacute;e :</strong> ${esc(p.date_pesee)} &nbsp;|&nbsp; <strong>Op&eacute;rateur :</strong> ${esc(p.operateur)}</p>
        <p><strong>Certificat SOLAS :</strong> ${esc(p.certificat_solas)}</p>
        <p style="margin-top:48px">Signature de l'op&eacute;rateur du pont-bascule : ______________________</p>
        <script>window.print()</script>
      </body></html>`);
    win.document.close();
  };

  const filtered = pesees.filter(p => {
    const q = search.toLowerCase();
    return (
      p.numero_conteneur.toLowerCase().includes(q) ||
      p.numero_ticket.toLowerCase().includes(q) ||
      p.camion_immatriculation.toLowerCase().includes(q)
    );
  });

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-4 sm:p-6 pb-24 text-slate-100">
      {/* Navigation Breadcrumb */}
      <div className="flex items-center gap-2 text-xs text-slate-400">
        <Link href="/port-operations" className="hover:text-emerald-400 flex items-center gap-1">
          <ArrowLeft className="w-3.5 h-3.5" /> {t('Opérations Portuaires', 'Port Operations')}
        </Link>
        <span>/</span>
        <span className="text-white">{t('Pont-Bascule & Pesage VGM (SOLAS)', 'Weighbridge & VGM Weighing (SOLAS)')}</span>
      </div>

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 bg-slate-900/80 p-6 rounded-2xl border border-slate-800 backdrop-blur-xl">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-emerald-500/10 text-emerald-400 rounded-xl border border-emerald-500/20">
            <Scale className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
              {t('Pont-Bascule & Certification VGM SOLAS', 'Weighbridge & SOLAS VGM Certification')}
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 font-mono">
                KACC_VGM
              </span>
            </h1>
            <p className="text-sm text-slate-400">
              {t('Contrôle pondéral réglementaire OMI SOLAS VI/2, calcul tare/net et émission des tickets certifiés VGM', 'IMO SOLAS VI/2 regulatory weight control, tare/net calculation and certified VGM ticket issuance')}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setIsModalOpen(true)}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-medium text-sm shadow-lg shadow-emerald-600/30 transition"
          >
            <Plus className="w-4 h-4" />
            {t('Effectuer une Pesée', 'Perform a Weighing')}
          </button>
        </div>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800">
          <span className="text-xs text-slate-400 uppercase font-semibold">{t('Pesées Réalisées', 'Weighings Performed')}</span>
          <p className="text-xl font-bold text-white mt-1">{pesees.length}</p>
        </div>
        <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800">
          <span className="text-xs text-slate-400 uppercase font-semibold">{t('Tonnage Certifié', 'Certified Tonnage')}</span>
          <p className="text-xl font-bold text-emerald-400 mt-1">
            {(pesees.reduce((acc, p) => acc + p.masse_vgm, 0) / 1000).toFixed(1)} {t('Tonnes', 'Tonnes')}
          </p>
        </div>
        <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800">
          <span className="text-xs text-slate-400 uppercase font-semibold">{t('Conformité SOLAS', 'SOLAS Compliance')}</span>
          <p className="text-xl font-bold text-blue-400 mt-1">
            {pesees.length > 0
              ? `${Math.round((pesees.filter(p => p.tolerance_conforme).length / pesees.length) * 100)}%`
              : '0%'}
          </p>
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
              placeholder={t('Rechercher par N° conteneur, ticket, camion...', 'Search by container No., ticket, truck...')}
              className="w-full pl-9 pr-4 py-2 text-sm bg-slate-800/90 border border-slate-700 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:border-emerald-500 font-mono"
            />
          </div>
        </div>

        {filtered.length === 0 ? (
          <div className="py-16 text-center bg-slate-950/40 rounded-xl border border-dashed border-slate-800">
            <Scale className="w-12 h-12 text-slate-400 mx-auto mb-3" />
            <h3 className="text-base font-semibold text-white">
              {pesees.length === 0
                ? t('Aucun ticket de pesée enregistré', 'No weighing ticket recorded')
                : t('Aucun résultat pour cette recherche', 'No result for this search')}
            </h3>
            {pesees.length === 0 && (
              <>
                <p className="text-sm text-slate-400 max-w-md mx-auto mt-1 mb-4">
                  {t('Le pont-bascule n\'a pas encore enregistré de passage de camion. Effectuez la première pesée d\'un conteneur pour générer son certificat officiel VGM.', 'The weighbridge has not recorded any truck yet. Perform the first container weighing to generate its official VGM certificate.')}
                </p>
                <button
                  onClick={() => setIsModalOpen(true)}
                  className="inline-flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-medium rounded-xl shadow transition"
                >
                  <Plus className="w-4 h-4" />
                  {t('Enregistrer une première pesée', 'Record the first weighing')}
                </button>
              </>
            )}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="bg-slate-800/60 text-slate-400 text-xs uppercase font-medium">
                <tr>
                  <th className="py-3 px-4 rounded-l-xl">{t('N° Ticket', 'Ticket No.')}</th>
                  <th className="py-3 px-4">{t('N° Conteneur', 'Container No.')}</th>
                  <th className="py-3 px-4">{t('Type', 'Type')}</th>
                  <th className="py-3 px-4">{t('Poids Brut / Tare', 'Gross / Tare')}</th>
                  <th className="py-3 px-4">{t('Masse VGM', 'VGM Mass')}</th>
                  <th className="py-3 px-4">{t('Camion / Transport', 'Truck / Carrier')}</th>
                  <th className="py-3 px-4">{t('Certificat SOLAS', 'SOLAS Certificate')}</th>
                  <th className="py-3 px-4 rounded-r-xl text-right">{t('Action', 'Action')}</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {filtered.map(p => (
                  <tr key={p.id} className="hover:bg-slate-800/40 transition">
                    <td className="py-3.5 px-4 font-mono font-medium text-emerald-400">
                      {p.numero_ticket}
                    </td>
                    <td className="py-3.5 px-4 font-mono text-white font-bold">
                      {p.numero_conteneur}
                    </td>
                    <td className="py-3.5 px-4 text-xs text-slate-300">
                      {p.type_conteneur}
                    </td>
                    <td className="py-3.5 px-4 text-xs font-mono">
                      <span>{p.poids_brut.toLocaleString()} kg</span>
                      <span className="text-slate-400 block">{t('Tare', 'Tare')}: {p.tare.toLocaleString()} kg</span>
                    </td>
                    <td className="py-3.5 px-4 font-mono text-white font-bold">
                      {p.masse_vgm.toLocaleString()} kg
                    </td>
                    <td className="py-3.5 px-4 text-xs">
                      <span className="text-white block font-medium">{p.camion_immatriculation}</span>
                      <span className="text-slate-400">{p.transporteur}</span>
                    </td>
                    <td className="py-3.5 px-4">
                      <span className={`px-2.5 py-1 rounded-full text-xs font-semibold flex items-center gap-1 w-fit border ${p.tolerance_conforme
                          ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                          : 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                        }`}>
                        {p.tolerance_conforme ? <CheckCircle2 className="w-3 h-3" /> : <AlertTriangle className="w-3 h-3" />}
                        {p.certificat_solas}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <button
                        onClick={() => handlePrintVgm(p)}
                        className="p-1.5 hover:bg-slate-800 rounded text-slate-400 hover:text-white transition"
                        title={t('Imprimer Certificat VGM', 'Print VGM Certificate')}
                      >
                        <Printer className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Modal Pesée */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-lg w-full p-6 shadow-2xl">
            <h3 className="text-lg font-bold text-white mb-1 flex items-center gap-2">
              <Scale className="w-5 h-5 text-emerald-400" />
              {t('Nouvelle Pesée Pont-Bascule', 'New Weighbridge Weighing')}
            </h3>
            <p className="text-xs text-slate-400 mb-4">
              {t('Enregistrement officiel de la pesée et certification de la Masse Brute Vérifiée (VGM)', 'Official weighing record and Verified Gross Mass (VGM) certification')}
            </p>

            <form onSubmit={handleCreatePesee} className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-slate-300 mb-1">{t('N° Conteneur (ISO 6346) *', 'Container No. (ISO 6346) *')}</label>
                  <input
                    type="text"
                    required
                    value={formData.numero_conteneur}
                    onChange={e => setFormData({ ...formData, numero_conteneur: e.target.value })}
                    placeholder={t('Ex: MSKU 942851-2', 'e.g. MSKU 942851-2')}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-emerald-500 font-mono uppercase"
                  />
                </div>
                <div>
                  <label className="block text-xs text-slate-300 mb-1">{t('Type Conteneur', 'Container Type')}</label>
                  <select
                    value={formData.type_conteneur}
                    onChange={e => setFormData({ ...formData, type_conteneur: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-emerald-500"
                  >
                    <option value="20' Dry Standard">20' Dry Standard</option>
                    <option value="40' Dry Standard">40' Dry Standard</option>
                    <option value="40' High Cube">40' High Cube</option>
                    <option value="20' Reefer (Frigorifique)">{t("20' Reefer (Frigo)", "20' Reefer")}</option>
                    <option value="40' Reefer (Frigorifique)">{t("40' Reefer (Frigo)", "40' Reefer")}</option>
                    <option value="Tank (Citerne ISO)">{t('Tank (Citerne ISO)', 'Tank (ISO container)')}</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-slate-300 mb-1">{t('Poids Brut Mesuré (kg) *', 'Measured Gross Weight (kg) *')}</label>
                  <input
                    type="number"
                    required
                    min={0}
                    value={formData.poids_brut || ''}
                    onChange={e => setFormData({ ...formData, poids_brut: parseFloat(e.target.value) || 0 })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-emerald-500 font-mono"
                  />
                </div>
                <div>
                  <label className="block text-xs text-slate-300 mb-1">{t('Tare du Conteneur (kg) *', 'Container Tare (kg) *')}</label>
                  <input
                    type="number"
                    required
                    min={0}
                    value={formData.tare || ''}
                    onChange={e => setFormData({ ...formData, tare: parseFloat(e.target.value) || 0 })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-emerald-500 font-mono"
                  />
                </div>
              </div>

              <div className="p-3 bg-slate-950 rounded-xl border border-slate-800 text-xs">
                <div className="flex justify-between items-center text-slate-400">
                  <span>{t('Masse Nette Calculée (VGM) :', 'Computed Net Mass (VGM):')}</span>
                  <span className="text-emerald-400 font-mono font-bold text-sm">
                    {Math.max(0, formData.poids_brut - formData.tare).toLocaleString()} kg
                  </span>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-slate-300 mb-1">{t('Immatriculation Tracteur', 'Truck Registration')}</label>
                  <input
                    type="text"
                    value={formData.camion_immatriculation}
                    onChange={e => setFormData({ ...formData, camion_immatriculation: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-emerald-500 font-mono"
                  />
                </div>
                <div>
                  <label className="block text-xs text-slate-300 mb-1">{t('Société de Transport', 'Transport Company')}</label>
                  <input
                    type="text"
                    value={formData.transporteur}
                    onChange={e => setFormData({ ...formData, transporteur: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-emerald-500"
                  />
                </div>
              </div>

              <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  disabled={saving}
                  className="px-4 py-2 text-sm text-slate-400 hover:text-white disabled:opacity-50"
                >
                  {t('Annuler', 'Cancel')}
                </button>
                <button
                  type="submit"
                  disabled={saving}
                  className="px-5 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-medium rounded-xl shadow-lg transition disabled:opacity-60"
                >
                  {saving ? t('Calcul…', 'Computing…') : t('Valider & Générer Certificat VGM', 'Validate & Generate VGM Certificate')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
