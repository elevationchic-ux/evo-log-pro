'use client';

import React, { useCallback, useEffect, useState } from 'react';
import { toast } from 'sonner';
import Link from 'next/link';
import {
  Fuel, Plus, Search, ArrowLeft, CheckCircle2,
  AlertTriangle, Loader2, HelpCircle
} from 'lucide-react';
import { transportAPI } from '@/lib/api-client';
import { SEUIL_SURCONSOMMATION_L100, PRIX_GAZOLE_XAF } from '@/config/carburant';

interface TicketCarburant {
  id: number;
  numero_ticket: string | null;
  immatriculation: string | null;
  chauffeur: string | null;
  station: string | null;
  litres: number;
  prix_litre: number | null;
  cout: number;
  kilometrage: number | null;
  index_precedent: number | null;
  delta_km: number | null;
  conso_l100: number | null;
  date_plein: string | null;
  statut: string;
}

/**
 * Seuil de surveillance et prix pré-rempli viennent de `@/config/carburant`,
 * partagés avec le tableau de bord carburant. La consommation n'est affichée
 * que si les DEUX index (plein actuel et plein précédent) ont été relevés :
 * sans mesure de distance, aucun contrôle n'est publié et la ligne reste
 * « Non mesuré ».
 */

const FORMULAIRE_VIDE = {
  numero_ticket: '',
  immatriculation: '',
  chauffeur_id: '' as '' | number,
  station: 'TotalEnergies Bonabéri (Douala)',
  litres: 0,
  prix_litre_xaf: PRIX_GAZOLE_XAF,
  index_km: 0,
  index_precedent: 0,
  mode_paiement: 'especes',
};

const fmtNum = (n: number | null | undefined, digits = 0) =>
  n === null || n === undefined
    ? ''
    : new Intl.NumberFormat('fr-FR', { maximumFractionDigits: digits }).format(n);

const fmtDate = (iso: string | null) => {
  if (!iso) return '';
  const d = new Date(iso);
  return Number.isNaN(d.getTime()) ? '' : d.toLocaleDateString('fr-FR');
};

export default function SaisieTicketCarburantPage() {
  const [tickets, setTickets] = useState<TicketCarburant[]>([]);
  const [totaux, setTotaux] = useState({ litres: 0, cout: 0 });
  const [chauffeurs, setChauffeurs] = useState<{ id: number; libelle: string }[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const [formData, setFormData] = useState({ ...FORMULAIRE_VIDE });

  const loadTickets = useCallback(async () => {
    setLoading(true);
    try {
      const res = await transportAPI.getTicketsCarburant({ limit: 200 });
      const data = res.data || {};
      setTickets(Array.isArray(data.items) ? data.items : []);
      setTotaux({ litres: data.litres_total ?? 0, cout: data.cout_total ?? 0 });
    } catch {
      // Réseau indisponible : la liste reste vide, aucun ticket n'est simulé.
      setTickets([]);
      setTotaux({ litres: 0, cout: 0 });
      toast.error("Erreur réseau  les tickets carburant n'ont pas pu être chargés.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadTickets();
  }, [loadTickets]);

  useEffect(() => {
    transportAPI
      .getChauffeurs({ limit: 200 })
      .then(res => {
        const rows = Array.isArray(res.data) ? res.data : res.data?.items || [];
        setChauffeurs(
          rows.map((c: any) => ({
            id: c.id,
            libelle: `${c.nom ?? ''} ${c.prenom ?? ''}`.trim() || `Chauffeur #${c.id}`,
          }))
        );
      })
      .catch(() => setChauffeurs([]));
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    const immatriculation = formData.immatriculation.trim();
    if (!immatriculation) {
      toast.error('Immatriculation obligatoire : le ticket doit être rattaché à un véhicule.');
      return;
    }
    if (!formData.litres || formData.litres <= 0) {
      toast.error('Le litrage pris doit être supérieur à 0.');
      return;
    }
    setIsSubmitting(true);
    try {
      await transportAPI.createTicketCarburant({
        numero_ticket: formData.numero_ticket.trim() || null,
        immatriculation,
        chauffeur_id: formData.chauffeur_id === '' ? null : Number(formData.chauffeur_id),
        station: formData.station,
        litres: Number(formData.litres),
        prix_litre: Number(formData.prix_litre_xaf),
        kilometrage: formData.index_km ? Number(formData.index_km) : null,
        index_precedent: formData.index_precedent ? Number(formData.index_precedent) : null,
        mode_paiement: formData.mode_paiement,
      });
      toast.success('Ticket carburant enregistré et consommation contrôlée.');
      setIsModalOpen(false);
      setFormData({
        ...FORMULAIRE_VIDE,
        station: formData.station,
        prix_litre_xaf: formData.prix_litre_xaf,
      });
      loadTickets();
    } catch (err: any) {
      toast.error(
        err?.response?.data?.message ||
        err?.response?.data?.detail ||
        "Enregistrement refusé par le serveur."
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  const filtered = tickets.filter(t => {
    const q = search.toLowerCase();
    return (
      (t.immatriculation ?? '').toLowerCase().includes(q) ||
      (t.numero_ticket ?? '').toLowerCase().includes(q) ||
      (t.chauffeur ?? '').toLowerCase().includes(q)
    );
  });

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-4 sm:p-6 pb-24 text-slate-100">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-xs text-slate-400">
        <Link href="/transport-flotte/control-tower" className="hover:text-amber-400 flex items-center gap-1">
          <ArrowLeft className="w-3.5 h-3.5" /> Transport & Flotte
        </Link>
        <span>/</span>
        <span className="text-white">Saisie & Contrôle des Tickets Carburant</span>
      </div>

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 bg-slate-900/80 p-6 rounded-2xl border border-slate-800 backdrop-blur-xl">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-amber-500/10 text-amber-400 rounded-xl border border-amber-500/20">
            <Fuel className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
              Saisie des Tickets Carburant & Contrôle FuelGuard
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/30 font-mono">
                KTRN_FUL
              </span>
            </h1>
            <p className="text-sm text-slate-400">
              Enregistrement des prises de carburant en station, réconciliation des litrages et détection des anomalies
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <div className="text-right">
            <p className="text-xs text-slate-400">Total saisi</p>
            <p className="text-sm font-mono font-bold text-white">
              {fmtNum(totaux.litres)} L
              <span className="text-slate-400 font-normal"> / {fmtNum(totaux.cout)} XAF</span>
            </p>
          </div>
          <button
            onClick={() => setIsModalOpen(true)}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-amber-600 hover:bg-amber-500 text-white font-medium text-sm shadow-lg shadow-amber-600/30 transition"
          >
            <Plus className="w-4 h-4" />
            Saisir un Ticket Carburant
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
              placeholder="Rechercher ticket, camion, chauffeur..."
              className="w-full pl-9 pr-4 py-2 text-sm bg-slate-800/90 border border-slate-700 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:border-amber-500"
            />
          </div>
          <span className="text-xs text-slate-500">
            {tickets.length} ticket(s) enregistré(s)
          </span>
        </div>

        {loading ? (
          <div className="py-16 text-center text-slate-400">
            <Loader2 className="w-8 h-8 animate-spin mx-auto mb-3 text-amber-400" />
            <p className="text-sm">Chargement des tickets carburant...</p>
          </div>
        ) : filtered.length === 0 ? (
          <div className="py-16 text-center bg-slate-950/40 rounded-xl border border-dashed border-slate-800">
            <Fuel className="w-12 h-12 text-slate-400 mx-auto mb-3" />
            <h3 className="text-base font-semibold text-white">
              {tickets.length === 0
                ? 'Aucun ticket carburant enregistré'
                : 'Aucun ticket ne correspond à la recherche'}
            </h3>
            <p className="text-sm text-slate-400 max-w-md mx-auto mt-1 mb-4">
              {tickets.length === 0
                ? "Aucun plein de carburant n'avait encore été saisi pour votre structure. Enregistrez le premier ticket remis par vos conducteurs."
                : "Affinez la recherche sur l'immatriculation, le numéro de ticket ou le chauffeur."}
            </p>
            {tickets.length === 0 && (
              <button
                onClick={() => setIsModalOpen(true)}
                className="inline-flex items-center gap-2 px-4 py-2 bg-amber-600 hover:bg-amber-500 text-white text-sm font-medium rounded-xl shadow transition"
              >
                <Plus className="w-4 h-4" />
                Saisir un premier ticket
              </button>
            )}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="bg-slate-800/60 text-slate-400 text-xs uppercase font-medium">
                <tr>
                  <th className="py-3 px-4 rounded-l-xl">N° Ticket</th>
                  <th className="py-3 px-4">Véhicule</th>
                  <th className="py-3 px-4">Chauffeur</th>
                  <th className="py-3 px-4">Station Service</th>
                  <th className="py-3 px-4">Litrages & Prix</th>
                  <th className="py-3 px-4">Total (XAF)</th>
                  <th className="py-3 px-4">Conso. Calculée</th>
                  <th className="py-3 px-4 rounded-r-xl">Contrôle FuelGuard</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {filtered.map(t => (
                  <tr key={t.id} className="hover:bg-slate-800/40 transition">
                    <td className="py-3.5 px-4 font-mono font-medium text-amber-400">
                      {t.numero_ticket || `#${t.id}`}
                      <span className="text-slate-500 block text-xs">
                        {fmtDate(t.date_plein)}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 font-semibold text-white">
                      {t.immatriculation || ''}
                    </td>
                    <td className="py-3.5 px-4 text-xs text-slate-300">
                      {t.chauffeur || 'Non rattaché'}
                    </td>
                    <td className="py-3.5 px-4 text-xs text-slate-400">
                      {t.station || ''}
                    </td>
                    <td className="py-3.5 px-4 font-mono text-xs">
                      <span className="text-white font-bold">{fmtNum(t.litres)} L</span>
                      <span className="text-slate-400 block">
                        à {fmtNum(t.prix_litre)} XAF/L
                      </span>
                    </td>
                    <td className="py-3.5 px-4 font-mono text-xs text-white font-bold">
                      {fmtNum(t.cout)} XAF
                    </td>
                    <td className="py-3.5 px-4 font-mono text-xs font-bold text-slate-200">
                      {t.conso_l100 === null || t.conso_l100 === undefined ? (
                        <span className="text-slate-500 font-normal">Non mesurée</span>
                      ) : (
                        <>{fmtNum(t.conso_l100, 1)} L/100km</>
                      )}
                      {t.delta_km ? (
                        <span className="text-slate-500 block text-xs font-normal">
                          sur {fmtNum(t.delta_km)} km
                        </span>
                      ) : null}
                    </td>
                    <td className="py-3.5 px-4">
                      {t.conso_l100 === null || t.conso_l100 === undefined ? (
                        <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-slate-800 text-slate-400 border border-slate-700 flex items-center gap-1 w-fit">
                          <HelpCircle className="w-3 h-3" />
                          Index incomplet
                        </span>
                      ) : t.conso_l100 > SEUIL_SURCONSOMMATION_L100 ? (
                        <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-red-500/10 text-red-400 border border-red-500/20 flex items-center gap-1 w-fit">
                          <AlertTriangle className="w-3 h-3" />
                          Surconsommation
                        </span>
                      ) : (
                        <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center gap-1 w-fit">
                          <CheckCircle2 className="w-3 h-3" />
                          Conforme
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Modal Saisie Ticket */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-lg w-full p-6 shadow-2xl">
            <h3 className="text-lg font-bold text-white mb-1 flex items-center gap-2">
              <Fuel className="w-5 h-5 text-amber-400" />
              Saisir un Ticket de Carburant
            </h3>
            <p className="text-xs text-slate-400 mb-4">
              Enregistrement de la prise de carburant et vérification du ratio kilométrique
            </p>

            <form onSubmit={handleCreate} className="space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-slate-300 mb-1">N° du Reçu / Ticket</label>
                  <input
                    type="text"
                    value={formData.numero_ticket}
                    onChange={e => setFormData({ ...formData, numero_ticket: e.target.value })}
                    placeholder="Ex: TCK-TOT-88412"
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-amber-500 font-mono"
                  />
                </div>
                <div>
                  <label className="block text-xs text-slate-300 mb-1">
                    Véhicule Poids Lourd *
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.immatriculation}
                    onChange={e => setFormData({ ...formData, immatriculation: e.target.value })}
                    placeholder="Ex: TR 4589 AB"
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-amber-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-slate-300 mb-1">Chauffeur</label>
                  <select
                    value={formData.chauffeur_id}
                    onChange={e =>
                      setFormData({
                        ...formData,
                        chauffeur_id: e.target.value === '' ? '' : Number(e.target.value),
                      })
                    }
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-amber-500"
                  >
                    <option value="">
                      {chauffeurs.length === 0 ? 'Aucun chauffeur enregistré' : 'Non rattaché'}
                    </option>
                    {chauffeurs.map(c => (
                      <option key={c.id} value={c.id}>
                        {c.libelle}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-xs text-slate-300 mb-1">Station Service</label>
                  <select
                    value={formData.station}
                    onChange={e => setFormData({ ...formData, station: e.target.value })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-amber-500"
                  >
                    <option value="TotalEnergies Bonabéri (Douala)">TotalEnergies Bonabéri</option>
                    <option value="Tradex Port Kribi">Tradex Port Kribi</option>
                    <option value="Tradex Bassa (Douala)">Tradex Bassa Douala</option>
                    <option value="Ola Energy limbé">Ola Energy limbé</option>
                    <option value="Cuve Interne Siège LPC SA">Cuve Interne Entreprise</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-slate-300 mb-1">Litres Pris (L) *</label>
                  <input
                    type="number"
                    step="0.1"
                    min="0"
                    required
                    value={formData.litres || ''}
                    onChange={e => setFormData({ ...formData, litres: parseFloat(e.target.value) || 0 })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-amber-500 font-mono"
                  />
                </div>
                <div>
                  <label className="block text-xs text-slate-300 mb-1">Prix au Litre (XAF)</label>
                  <input
                    type="number"
                    step="1"
                    min="0"
                    value={formData.prix_litre_xaf || ''}
                    onChange={e =>
                      setFormData({ ...formData, prix_litre_xaf: parseFloat(e.target.value) || 0 })
                    }
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-amber-500 font-mono"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-slate-300 mb-1">Index Compteur Précédent (km)</label>
                  <input
                    type="number"
                    min="0"
                    value={formData.index_precedent || ''}
                    onChange={e =>
                      setFormData({ ...formData, index_precedent: parseInt(e.target.value) || 0 })
                    }
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-amber-500 font-mono"
                  />
                </div>
                <div>
                  <label className="block text-xs text-slate-300 mb-1">Index Compteur Actuel (km)</label>
                  <input
                    type="number"
                    min="0"
                    value={formData.index_km || ''}
                    onChange={e => setFormData({ ...formData, index_km: parseInt(e.target.value) || 0 })}
                    className="w-full px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-amber-500 font-mono"
                  />
                </div>
              </div>

              <p className="text-[11px] text-slate-500">
                Les deux index sont indispensables au calcul de la consommation : sans eux, le
                contrôle FuelGuard reste sans mesure.
              </p>

              <div className="p-3 bg-slate-950 rounded-xl border border-slate-800 text-xs flex justify-between items-center">
                <span className="text-slate-400">Montant Total Plein :</span>
                <span className="font-mono text-amber-400 font-bold text-sm">
                  {fmtNum(formData.litres * formData.prix_litre_xaf)} XAF
                </span>
              </div>

              <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 text-sm text-slate-400 hover:text-white"
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-5 py-2 bg-amber-600 hover:bg-amber-500 disabled:opacity-60 text-white text-sm font-medium rounded-xl shadow-lg transition flex items-center gap-2"
                >
                  {isSubmitting && <Loader2 className="w-4 h-4 animate-spin" />}
                  Enregistrer & Contrôler
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
