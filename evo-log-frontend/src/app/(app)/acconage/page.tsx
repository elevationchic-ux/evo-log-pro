'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { acconageAPI } from '@/lib/api-client';
import { Anchor, Plus, Search, Ship, Package, X } from 'lucide-react';
import { toast } from 'sonner';

// Badge du statut reellement persiste sur l'operation. Une operation n'est
// jamais presentee comme terminee sans que la base le dise.
function statutBadge(statut?: string): string {
  const s = String(statut || '').toUpperCase();
  if (s === 'TERMINE') return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';
  if (s === 'EN_COURS') return 'bg-amber-500/10 text-amber-400 border-amber-500/20';
  if (s === 'ANNULE') return 'bg-rose-500/10 text-rose-400 border-rose-500/20';
  return 'bg-slate-500/10 text-slate-400 border-slate-500/20';
}

const TYPES_OPERATION = [
  { value: 'dechargement_conteneur', label: 'Déchargement conteneurs' },
  { value: 'chargement_conteneur', label: 'Chargement conteneurs' },
  { value: 'manutention_vrac', label: 'Manutention vrac' },
  { value: 'transbordement', label: 'Transbordement' },
  { value: 'arrimage', label: 'Arrimage / déarrimage' },
];

const UNITES = ['TEU', 'tonne', 'm³', 'colis', 'lot'];

export default function AcconagePage() {
  const [mounted, setMounted] = useState(false);
  const queryClient = useQueryClient();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  // Form states : uniquement des champs portés par la table operations_acconage
  const [escaleId, setEscaleId] = useState('');
  const [operationType, setOperationType] = useState('dechargement_conteneur');
  const [marchandise, setMarchandise] = useState('');
  const [quantite, setQuantite] = useState('');
  const [unite, setUnite] = useState('TEU');
  const [equipement, setEquipement] = useState('');
  const [notes, setNotes] = useState('');

  useEffect(() => {
    setMounted(true);
  }, []);

  const { data, isLoading } = useQuery({
    queryKey: ['acconage'],
    queryFn: async () => {
      const res = await acconageAPI.getAcconages();
      return res.data?.items || res.data || (Array.isArray(res) ? res : []);
    },
    enabled: mounted,
  });

  // Escales existantes : une opération d'acconage ne peut être enregistrée que
  // sur une escale déjà présente au port (aucune escale créée à la volée).
  const { data: escalesData, isLoading: escalesLoading } = useQuery({
    queryKey: ['acconage-escales'],
    queryFn: async () => {
      const res = await acconageAPI.getEscales();
      return res.data?.items || res.data || (Array.isArray(res) ? res : []);
    },
    enabled: mounted && isModalOpen,
  });

  // L'API des escales ne porte que navire_id : la désignation du navire vient
  // de la table navires, mise en correspondance ici (aucun nom inventé).
  const { data: naviresData } = useQuery({
    queryKey: ['acconage-navires'],
    queryFn: async () => {
      const res = await acconageAPI.getNavires();
      return res.data?.items || res.data || (Array.isArray(res) ? res : []);
    },
    enabled: mounted && isModalOpen,
  });

  const escales = Array.isArray(escalesData) ? escalesData : [];
  const nomsNavires: Record<number, string> = Array.isArray(naviresData)
    ? naviresData.reduce((acc: Record<number, string>, n: any) => {
        if (n?.id != null && n?.nom) acc[n.id] = n.nom;
        return acc;
      }, {})
    : {};

  const createMutation = useMutation({
    mutationFn: async (payload: any) => {
      const res = await acconageAPI.createAcconage(payload);
      return res.data;
    },
    onSuccess: () => {
      toast.success("Opération d'acconage enregistrée avec succès !");
      queryClient.invalidateQueries({ queryKey: ['acconage'] });
      setIsModalOpen(false);
      setEscaleId('');
      setMarchandise('');
      setQuantite('');
      setEquipement('');
      setNotes('');
    },
    onError: (err: any) => {
      const detail = err?.response?.data?.detail;
      toast.error(
        typeof detail === 'string'
          ? detail
          : "Erreur lors de l'enregistrement de l'opération."
      );
    },
  });

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    createMutation.mutate({
      escale_id: Number(escaleId),
      type_operation: operationType,
      marchandise: marchandise.trim() || null,
      quantite: quantite === '' ? null : Number(quantite),
      unite: unite,
      equipement: equipement.trim() || null,
      notes: notes.trim() || null,
    });
  };

  if (!mounted) return <div className="p-8 text-center text-slate-500">Chargement du module K-Acconage...</div>;

  const items = Array.isArray(data) ? data : [];
  const filteredItems = items.filter((i: any) =>
    (String(i.nom_navire || '') + ' ' + String(i.numero_escale || '') + ' ' + String(i.type_operation || ''))
      .toLowerCase()
      .includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6 sm:space-y-8 max-w-7xl mx-auto animate-in fade-in duration-500 text-white">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-sky-500/10 text-sky-400 text-xs font-semibold mb-2 border border-sky-500/20">
            <Anchor className="w-3.5 h-3.5" />
            K-Acconage • Gestion de Quai & Manutention Portuaire
          </div>
          <h1 className="text-2xl sm:text-3xl font-black tracking-tight">Manutention & Operations de Quai</h1>
          <p className="text-slate-400 text-sm mt-1">Suivi des chargements, déchargements et grutage au Port de Douala.</p>
        </div>

        <button
          onClick={() => setIsModalOpen(true)}
          className="inline-flex items-center justify-center gap-2 bg-sky-600 hover:bg-sky-500 text-white font-semibold px-5 py-3 rounded-xl text-sm shadow-lg shadow-sky-600/30 transition-all hover:scale-[1.02]"
        >
          <Plus className="w-4 h-4" />
          Enregistrer une Opération
        </button>
      </div>

      {/* Table Section */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl shadow-xl overflow-hidden">
        <div className="p-4 sm:p-6 border-b border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <h3 className="text-base sm:text-lg font-bold text-slate-100">
            Journal des Opérations d'Acconage
          </h3>

          <div className="relative w-full sm:w-72">
            <Search className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Rechercher par navire ou escale..."
              className="w-full pl-9 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-sky-500"
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-slate-950 text-xs font-bold text-slate-400 uppercase tracking-wider border-b border-slate-800">
              <tr>
                <th className="px-6 py-4">Navire / Escale</th>
                <th className="px-6 py-4">Type d'Opération</th>
                <th className="px-6 py-4">Marchandise traitée</th>
                <th className="px-6 py-4 text-right">Statut Quai</th>
                <th className="px-6 py-4 text-right">Fiche</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {isLoading ? (
                <tr><td colSpan={5} className="p-12 text-center text-slate-400">Chargement de l'acconage...</td></tr>
              ) : filteredItems.length === 0 ? (
                <tr><td colSpan={5} className="p-8 text-center text-slate-500">Aucune opération d'acconage trouvée.</td></tr>
              ) : (
                filteredItems.map((item: any, idx: number) => (
                  <tr key={item.id || idx} className="hover:bg-slate-800/40 transition-colors">
                    <td className="px-6 py-4 font-bold text-slate-100">
                      <div className="flex items-center gap-2">
                        <Ship className="w-4 h-4 text-sky-400 shrink-0" />
                        <span>{item.nom_navire || 'Navire non rattaché'}</span>
                      </div>
                      <div className="ml-6 text-xs font-mono text-slate-500">
                        {item.numero_escale || 'escale non rattachée'}
                        {item.quai ? ` • ${item.quai}` : ''}
                      </div>
                    </td>
                    <td className="px-6 py-4 font-semibold text-slate-200 capitalize">
                      {item.type_operation || '—'}
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2 text-slate-300">
                        <Package className="w-4 h-4 text-slate-500 shrink-0" />
                        <span>{item.marchandise || 'Non renseignée'}</span>
                      </div>
                      {item.quantite != null && (
                        <div className="ml-6 text-xs font-mono text-sky-400">
                          {item.quantite} {item.unite || ''}
                        </div>
                      )}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold border ${statutBadge(item.statut)}`}>
                        {(item.statut || 'planifie').replace(/_/g, ' ').toUpperCase()}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right whitespace-nowrap">
                      <Link
                        href={`/acconage/view?id=${item.id}`}
                        className="text-xs font-semibold text-sky-400 hover:text-sky-300"
                      >
                        Ouvrir
                      </Link>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-lg p-6 text-white shadow-2xl animate-in zoom-in-95 duration-200 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between pb-4 border-b border-slate-800">
              <h3 className="text-lg font-bold">Enregistrement Opération Acconage</h3>
              <button onClick={() => setIsModalOpen(false)} className="text-slate-400 hover:text-slate-200">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreate} className="space-y-4 pt-4">
              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase mb-1">Escale concernée *</label>
                {escalesLoading ? (
                  <div className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-500">
                    Chargement des escales...
                  </div>
                ) : escales.length === 0 ? (
                  <div className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-400">
                    Aucune escale enregistrée au port. Créez d'abord l'escale dans
                    le module Escales & Navires.
                  </div>
                ) : (
                  <select
                    required
                    value={escaleId}
                    onChange={(e) => setEscaleId(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-sky-500"
                  >
                    <option value="">— Sélectionner une escale —</option>
                    {escales.map((es: any) => (
                      <option key={es.id} value={es.id}>
                        {es.numero_escale}
                        {nomsNavires[es.navire_id] ? ` • ${nomsNavires[es.navire_id]}` : ''}
                      </option>
                    ))}
                  </select>
                )}
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase mb-1">Type d'Opération *</label>
                <select
                  value={operationType}
                  onChange={(e) => setOperationType(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-sky-500"
                >
                  {TYPES_OPERATION.map((t) => (
                    <option key={t.value} value={t.value}>{t.label}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase mb-1">Marchandise manutentionnée</label>
                <input
                  type="text"
                  value={marchandise}
                  onChange={(e) => setMarchandise(e.target.value)}
                  placeholder="ex: Sacs de ciment, bananes, pièces détachées"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-sky-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 uppercase mb-1">Quantité traitée</label>
                  <input
                    type="number"
                    min={0}
                    step="0.01"
                    value={quantite}
                    onChange={(e) => setQuantite(e.target.value)}
                    placeholder="ex: 420"
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-sky-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-400 uppercase mb-1">Unité</label>
                  <select
                    value={unite}
                    onChange={(e) => setUnite(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-sky-500"
                  >
                    {UNITES.map((u) => (
                      <option key={u} value={u}>{u}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase mb-1">Équipement de quai affecté</label>
                <input
                  type="text"
                  value={equipement}
                  onChange={(e) => setEquipement(e.target.value)}
                  placeholder="ex: Portique STS 02, Grue Gottwald #1"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-sky-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase mb-1">Remarques d'exploitation</label>
                <textarea
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="ex: Rotation sous séquestre, équipe de 12 dockers"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-sky-500 h-20"
                />
              </div>

              <div className="flex justify-end gap-3 pt-4 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 rounded-xl text-sm font-semibold text-slate-400 hover:text-slate-200"
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  disabled={createMutation.isPending || !escaleId}
                  className="px-5 py-2.5 rounded-xl text-sm font-semibold bg-sky-600 hover:bg-sky-500 text-white shadow-lg shadow-sky-600/30 disabled:opacity-50"
                >
                  {createMutation.isPending ? 'Enregistrement...' : "Valider L'Opération"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
