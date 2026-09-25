'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  Receipt, PlusCircle, CheckCircle2, Clock, AlertTriangle,
  RefreshCw, DollarSign, Wallet, Check, X, ShieldAlert,
  FileText, Calendar, MapPin, Tag, Download, UserCheck
} from 'lucide-react';
import { fraisMissionsAPI } from '@/lib/api-client';
import { toast } from 'sonner';

interface FraisItem {
  id: number;
  user_id?: number;
  nom_collaborateur?: string;
  titre_mission?: string;
  type_frais: string;
  montant: number;
  devise: string;
  date_depense?: string;
  fournisseur?: string;
  ville_lieu?: string;
  justificatif_url?: string;
  numero_recu?: string;
  statut: string;
  commentaire?: string;
  valide_par_nom?: string;
  motif_rejet?: string;
  created_at?: string;
}

interface AvanceItem {
  id: number;
  nom_collaborateur?: string;
  titre_mission: string;
  corridor_destination?: string;
  montant_demande: number;
  montant_accorde: number;
  devise: string;
  motif?: string;
  statut: string;
  created_at?: string;
}

export default function PortailFraisPage() {
  const [activeTab, setActiveTab] = useState<'frais' | 'nouveau' | 'avances' | 'validation'>('frais');
  const [fraisList, setFraisList] = useState<FraisItem[]>([]);
  const [avancesList, setAvancesList] = useState<AvanceItem[]>([]);
  const [stats, setStats] = useState({
    nb_frais_total: 0,
    total_engage_xaf: 0,
    total_valide_xaf: 0,
    total_en_attente_xaf: 0,
    total_avances_accordees_xaf: 0,
    solde_a_regulariser_xaf: 0,
  });
  const [loading, setLoading] = useState(true);

  // Formulaire nouveau frais
  const [formFrais, setFormFrais] = useState({
    titre_mission: 'Mission Corridor Douala - N’Djamena',
    type_frais: 'PEAGE',
    montant: '',
    fournisseur: 'Poste de Péage Edéa',
    ville_lieu: 'Edéa',
    numero_recu: 'REC-2026-0941',
    commentaire: '',
  });
  const [submittingFrais, setSubmittingFrais] = useState(false);

  // Formulaire nouvelle avance
  const [formAvance, setFormAvance] = useState({
    titre_mission: '',
    corridor_destination: 'Douala - Bangui',
    montant_demande: '',
    motif: 'Avance carburant et péages pour convoi exceptionnel 3 camions',
  });
  const [submittingAvance, setSubmittingAvance] = useState(false);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [resFrais, resAvances, resStats] = await Promise.all([
        fraisMissionsAPI.getAll(),
        fraisMissionsAPI.getAvances(),
        fraisMissionsAPI.getStats(),
      ]);

      if (resFrais.data) {
        setFraisList(resFrais.data.items || []);
      }
      if (resAvances.data) {
        setAvancesList(resAvances.data.items || []);
      }
      if (resStats.data) {
        setStats(resStats.data);
      }
    } catch (err: any) {
      toast.error('Impossible de charger les notes de frais');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleCreateFrais = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmittingFrais(true);
    try {
      await fraisMissionsAPI.create({
        ...formFrais,
        montant: parseFloat(formFrais.montant),
      });
      toast.success('Note de frais soumise pour validation');
      setFormFrais({
        titre_mission: 'Mission Corridor Douala - N’Djamena',
        type_frais: 'PEAGE',
        montant: '',
        fournisseur: '',
        ville_lieu: '',
        numero_recu: '',
        commentaire: '',
      });
      setActiveTab('frais');
      fetchData();
    } catch (err: any) {
      toast.error('Erreur lors de la soumission de la note de frais');
    } finally {
      setSubmittingFrais(false);
    }
  };

  const handleCreateAvance = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmittingAvance(true);
    try {
      await fraisMissionsAPI.createAvance({
        ...formAvance,
        montant_demande: parseFloat(formAvance.montant_demande),
      });
      toast.success('Demande d’avance de mission enregistrée');
      setFormAvance({
        titre_mission: '',
        corridor_destination: 'Douala - Bangui',
        montant_demande: '',
        motif: '',
      });
      fetchData();
    } catch (err: any) {
      toast.error('Erreur enregistrement avance');
    } finally {
      setSubmittingAvance(false);
    }
  };

  const handleValidateFrais = async (id: number, action: 'VALIDER' | 'REJETER') => {
    try {
      await fraisMissionsAPI.validate(id, action, 'Manager Terrain');
      toast.success(`Note de frais ${action === 'VALIDER' ? 'approuvée' : 'rejetée'}`);
      fetchData();
    } catch (err: any) {
      toast.error('Erreur lors du traitement de la note de frais');
    }
  };

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="bg-gradient-to-r from-slate-900 via-emerald-950 to-slate-900 rounded-3xl p-6 sm:p-8 text-white border border-emerald-900/40 shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="space-y-2">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 text-xs font-bold uppercase tracking-wider">
            <Receipt className="w-3.5 h-3.5" /> Portail Frais & Missions
          </div>
          <h1 className="text-2xl sm:text-3xl font-black tracking-tight">
            Notes de Frais, Avances & Déplacements
          </h1>
          <p className="text-sm text-slate-300">
            Gestion dématérialisée de vos dépenses professionnelles terrain, péages, hébergement et indemnités de route.
          </p>
        </div>

        <button
          onClick={fetchData}
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-white text-xs font-bold border border-slate-700 transition-colors shadow-sm self-start md:self-auto"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          Actualiser
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-700 shadow-sm space-y-1">
          <span className="text-xs font-bold text-slate-500 uppercase">Total Frais Engagés</span>
          <div className="text-xl font-black text-slate-200">
            {stats.total_engage_xaf.toLocaleString()} XAF
          </div>
          <span className="text-[11px] text-slate-500">{stats.nb_frais_total} note(s) saisie(s)</span>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-700 shadow-sm space-y-1">
          <span className="text-xs font-bold text-emerald-600 uppercase">Frais Approuvés</span>
          <div className="text-xl font-black text-emerald-600">
            {stats.total_valide_xaf.toLocaleString()} XAF
          </div>
          <span className="text-[11px] text-emerald-300">Validé pour remboursement</span>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-700 shadow-sm space-y-1">
          <span className="text-xs font-bold text-amber-600 uppercase">En Attente Validation</span>
          <div className="text-xl font-black text-amber-600">
            {stats.total_en_attente_xaf.toLocaleString()} XAF
          </div>
          <span className="text-[11px] text-amber-300">En cours de revue manager</span>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-700 shadow-sm space-y-1">
          <span className="text-xs font-bold text-indigo-600 uppercase">Avances Accordées</span>
          <div className="text-xl font-black text-indigo-600">
            {stats.total_avances_accordees_xaf.toLocaleString()} XAF
          </div>
          <span className="text-[11px] text-indigo-300">Solde net : {stats.solde_a_regulariser_xaf.toLocaleString()} XAF</span>
        </div>
      </div>

      {/* Onglets */}
      <div className="flex overflow-x-auto gap-2 p-1.5 bg-slate-900 rounded-2xl border border-slate-700">
        {[
          { id: 'frais', label: 'Mes Notes de Frais', icon: FileText, count: fraisList.length },
          { id: 'nouveau', label: '+ Nouvelle Dépense', icon: PlusCircle },
          { id: 'avances', label: 'Demandes d’Avances', icon: Wallet, count: avancesList.length },
          { id: 'validation', label: 'Validation Manager', icon: UserCheck },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-2 px-4 py-3 rounded-xl text-xs sm:text-sm font-bold whitespace-nowrap transition-all ${
                isActive
                  ? 'bg-slate-900 text-slate-200 shadow-md border border-slate-700'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-white/10'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{tab.label}</span>
              {tab.count !== undefined && (
                <span className={`px-2 py-0.5 rounded-full text-[11px] font-mono ${
                  isActive ? 'bg-slate-900 text-white' : 'bg-slate-700 text-slate-300'
                }`}>
                  {tab.count}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Onglet 1 : Mes Notes de Frais */}
      {activeTab === 'frais' && (
        <div className="bg-slate-900 rounded-2xl border border-slate-700 overflow-hidden shadow-sm">
          <div className="p-4 border-b border-slate-700 flex items-center justify-between">
            <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider">
              Historique de vos dépenses ({fraisList.length})
            </h2>
            <button
              onClick={() => setActiveTab('nouveau')}
              className="px-3 py-1.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold transition-colors shadow-sm"
            >
              + Ajouter une dépense
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-800 border-b border-slate-700 text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                  <th className="p-3.5">Date & Réf</th>
                  <th className="p-3.5">Mission / Objet</th>
                  <th className="p-3.5">Catégorie</th>
                  <th className="p-3.5">Fournisseur & Lieu</th>
                  <th className="p-3.5">Montant</th>
                  <th className="p-3.5">Statut</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800 text-xs">
                {fraisList.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="p-8 text-center text-slate-500">
                      Aucune note de frais enregistrée pour le moment.
                    </td>
                  </tr>
                ) : (
                  fraisList.map((f) => (
                    <tr key={f.id} className="hover:bg-slate-800/80 transition-colors">
                      <td className="p-3.5">
                        <div className="font-bold text-slate-200">#{f.numero_recu || `FR-${f.id}`}</div>
                        <div className="text-[10px] text-slate-400">
                          {f.created_at ? new Date(f.created_at).toLocaleDateString() : 'Aujourd’hui'}
                        </div>
                      </td>
                      <td className="p-3.5 font-medium text-slate-200">
                        {f.titre_mission || 'Mission générale'}
                      </td>
                      <td className="p-3.5">
                        <span className="px-2.5 py-1 rounded-full text-[10px] font-bold bg-slate-900 text-slate-300 border border-slate-700">
                          {f.type_frais}
                        </span>
                      </td>
                      <td className="p-3.5 text-slate-400">
                        <div>{f.fournisseur || 'Comptant'}</div>
                        <div className="text-[10px] text-slate-400">{f.ville_lieu || 'Cameroun'}</div>
                      </td>
                      <td className="p-3.5 font-mono font-bold text-slate-200">
                        {f.montant.toLocaleString()} {f.devise}
                      </td>
                      <td className="p-3.5">
                        <span className={`px-2.5 py-1 rounded-full text-[10px] font-bold ${
                          f.statut === 'VALIDE' ? 'bg-emerald-500/15 text-emerald-300' :
                          f.statut === 'REJETE' ? 'bg-rose-500/15 text-rose-300' : 'bg-amber-500/15 text-amber-300'
                        }`}>
                          {f.statut}
                        </span>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Onglet 2 : Nouvelle Dépense */}
      {activeTab === 'nouveau' && (
        <div className="bg-slate-900 rounded-2xl border border-slate-700 p-6 max-w-2xl mx-auto shadow-sm space-y-6">
          <div className="pb-4 border-b border-slate-700">
            <h2 className="text-lg font-bold text-slate-200 flex items-center gap-2">
              <PlusCircle className="w-5 h-5 text-emerald-600" /> Saisie d’une Note de Frais Terrain
            </h2>
            <p className="text-xs text-slate-500">
              Ventilez vos dépenses engagées au cours de vos missions ou déplacements.
            </p>
          </div>

          <form onSubmit={handleCreateFrais} className="space-y-4">
            <div>
              <label className="text-xs font-bold text-slate-300 block mb-1">Mission / Contexte</label>
              <input
                type="text"
                required
                value={formFrais.titre_mission}
                onChange={(e) => setFormFrais({ ...formFrais, titre_mission: e.target.value })}
                className="w-full px-3 py-2 rounded-xl border border-slate-600 text-xs focus:ring-2 focus:ring-emerald-500 outline-none"
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="text-xs font-bold text-slate-300 block mb-1">Catégorie de Dépense</label>
                <select
                  value={formFrais.type_frais}
                  onChange={(e) => setFormFrais({ ...formFrais, type_frais: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl border border-slate-600 text-xs focus:ring-2 focus:ring-emerald-500 outline-none"
                >
                  <option value="PEAGE">Péages & Pesages Routiers</option>
                  <option value="CARBURANT">Carburant d’Appoint</option>
                  <option value="HEBERGEMENT">Hôtel / Hébergement Étape</option>
                  <option value="RESTAURATION">Restauration / Per Diem</option>
                  <option value="MANUTENTION">Frais de Manutention Quai</option>
                  <option value="PIECE_SECOURS">Dépannage / Pièce de Secours</option>
                  <option value="DIVERS">Autre Dépense Justifiée</option>
                </select>
              </div>

              <div>
                <label className="text-xs font-bold text-slate-300 block mb-1">Montant (XAF)</label>
                <input
                  type="number"
                  inputMode="numeric"
                  required
                  placeholder="Ex: 25000"
                  value={formFrais.montant}
                  onChange={(e) => setFormFrais({ ...formFrais, montant: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl border border-slate-600 text-xs focus:ring-2 focus:ring-emerald-500 outline-none"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="text-xs font-bold text-slate-300 block mb-1">Fournisseur / Établissement</label>
                <input
                  type="text"
                  placeholder="Ex: Hôtel de la Paix"
                  value={formFrais.fournisseur}
                  onChange={(e) => setFormFrais({ ...formFrais, fournisseur: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl border border-slate-600 text-xs focus:ring-2 focus:ring-emerald-500 outline-none"
                />
              </div>

              <div>
                <label className="text-xs font-bold text-slate-300 block mb-1">Ville / Localité</label>
                <input
                  type="text"
                  placeholder="Ex: Bertoua, Garoua-Boulaï"
                  value={formFrais.ville_lieu}
                  onChange={(e) => setFormFrais({ ...formFrais, ville_lieu: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl border border-slate-600 text-xs focus:ring-2 focus:ring-emerald-500 outline-none"
                />
              </div>
            </div>

            <div>
              <label className="text-xs font-bold text-slate-300 block mb-1">N° Reçu / Facturette</label>
              <input
                type="text"
                placeholder="Ex: FACT-88910"
                value={formFrais.numero_recu}
                onChange={(e) => setFormFrais({ ...formFrais, numero_recu: e.target.value })}
                className="w-full px-3 py-2 rounded-xl border border-slate-600 text-xs focus:ring-2 focus:ring-emerald-500 outline-none"
              />
            </div>

            <div>
              <label className="text-xs font-bold text-slate-300 block mb-1">Commentaire / Justification</label>
              <textarea
                rows={2}
                placeholder="Précisez la raison de la dépense..."
                value={formFrais.commentaire}
                onChange={(e) => setFormFrais({ ...formFrais, commentaire: e.target.value })}
                className="w-full px-3 py-2 rounded-xl border border-slate-600 text-xs focus:ring-2 focus:ring-emerald-500 outline-none"
              />
            </div>

            <button
              type="submit"
              disabled={submittingFrais}
              className="w-full py-3 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold transition-colors shadow-sm"
            >
              {submittingFrais ? 'Transmission...' : 'Soumettre la note de frais'}
            </button>
          </form>
        </div>
      )}

      {/* Onglet 3 : Demandes d'Avances */}
      {activeTab === 'avances' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1 bg-slate-900 rounded-2xl border border-slate-700 p-6 space-y-4 shadow-sm">
            <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
              <Wallet className="w-4 h-4 text-indigo-600" /> Nouvelle Demande d’Avance
            </h3>

            <form onSubmit={handleCreateAvance} className="space-y-3">
              <div>
                <label className="text-xs font-bold text-slate-300 block mb-1">Titre de la Mission</label>
                <input
                  type="text"
                  required
                  placeholder="Ex: Escorte convoi N'Djamena"
                  value={formAvance.titre_mission}
                  onChange={(e) => setFormAvance({ ...formAvance, titre_mission: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl border border-slate-600 text-xs focus:ring-2 focus:ring-indigo-500 outline-none"
                />
              </div>

              <div>
                <label className="text-xs font-bold text-slate-300 block mb-1">Corridor / Destination</label>
                <input
                  type="text"
                  required
                  value={formAvance.corridor_destination}
                  onChange={(e) => setFormAvance({ ...formAvance, corridor_destination: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl border border-slate-600 text-xs focus:ring-2 focus:ring-indigo-500 outline-none"
                />
              </div>

              <div>
                <label className="text-xs font-bold text-slate-300 block mb-1">Montant Demandé (XAF)</label>
                <input
                  type="number"
                  inputMode="numeric"
                  required
                  placeholder="Ex: 150000"
                  value={formAvance.montant_demande}
                  onChange={(e) => setFormAvance({ ...formAvance, montant_demande: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl border border-slate-600 text-xs focus:ring-2 focus:ring-indigo-500 outline-none"
                />
              </div>

              <div>
                <label className="text-xs font-bold text-slate-300 block mb-1">Motif / Prévisionnel</label>
                <textarea
                  rows={3}
                  value={formAvance.motif}
                  onChange={(e) => setFormAvance({ ...formAvance, motif: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl border border-slate-600 text-xs focus:ring-2 focus:ring-indigo-500 outline-none"
                />
              </div>

              <button
                type="submit"
                disabled={submittingAvance}
                className="w-full py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold transition-colors shadow-sm"
              >
                {submittingAvance ? 'Envoi...' : 'Demander l’avance'}
              </button>
            </form>
          </div>

          <div className="lg:col-span-2 bg-slate-900 rounded-2xl border border-slate-700 overflow-hidden shadow-sm">
            <div className="p-4 border-b border-slate-700">
              <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider">
                Vos Demandes d’Avances ({avancesList.length})
              </h3>
            </div>

            <div className="divide-y divide-slate-800">
              {avancesList.length === 0 ? (
                <div className="p-8 text-center text-slate-500 text-xs">
                  Aucune demande d’avance enregistrée.
                </div>
              ) : (
                avancesList.map((a) => (
                  <div key={a.id} className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:bg-slate-800/80">
                    <div className="space-y-1">
                      <div className="text-xs font-bold text-slate-200">{a.titre_mission}</div>
                      <div className="text-[11px] text-slate-500">Destination : {a.corridor_destination || 'Cameroun'}</div>
                      <div className="text-[10px] text-slate-400">{a.motif}</div>
                    </div>
                    <div className="text-right space-y-1">
                      <div className="text-sm font-mono font-bold text-slate-200">
                        {a.montant_demande.toLocaleString()} {a.devise}
                      </div>
                      <span className={`inline-block px-2.5 py-0.5 rounded-full text-[10px] font-bold ${
                        a.statut === 'ACCORDEE' ? 'bg-emerald-500/15 text-emerald-300' : 'bg-amber-500/15 text-amber-300'
                      }`}>
                        {a.statut}
                      </span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}

      {/* Onglet 4 : Validation Manager & Comptabilité */}
      {activeTab === 'validation' && (
        <div className="bg-slate-900 rounded-2xl border border-slate-700 overflow-hidden shadow-sm">
          <div className="p-4 border-b border-slate-700">
            <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
              <UserCheck className="w-4 h-4 text-indigo-600" /> Approbation Hiérarchique & Rapprochement Comptable
            </h2>
            <p className="text-xs text-slate-500">
              Validez ou rejetez les notes de frais soumises par votre équipe terrain.
            </p>
          </div>

          <div className="divide-y divide-slate-800">
            {fraisList.filter(f => f.statut === 'SOUMIS').length === 0 ? (
              <div className="p-8 text-center text-slate-500 text-xs">
                Aucune note de frais en attente de validation.
              </div>
            ) : (
              fraisList.filter(f => f.statut === 'SOUMIS').map((f) => (
                <div key={f.id} className="p-4 flex flex-col md:flex-row md:items-center justify-between gap-4 hover:bg-slate-800/80">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold text-slate-200">#{f.numero_recu || `FR-${f.id}`}</span>
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-900 text-slate-400">
                        {f.type_frais}
                      </span>
                    </div>
                    <div className="text-xs text-slate-300 font-medium">{f.titre_mission}</div>
                    <div className="text-[11px] text-slate-500">{f.fournisseur} • {f.ville_lieu}</div>
                  </div>

                  <div className="flex items-center gap-4">
                    <div className="text-right">
                      <div className="text-sm font-mono font-bold text-slate-200">
                        {f.montant.toLocaleString()} {f.devise}
                      </div>
                      <span className="text-[10px] text-amber-600 font-bold">À valider</span>
                    </div>

                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => handleValidateFrais(f.id, 'VALIDER')}
                        className="px-3 py-1.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold transition-colors flex items-center gap-1"
                      >
                        <Check className="w-3.5 h-3.5" /> Approuver
                      </button>
                      <button
                        onClick={() => handleValidateFrais(f.id, 'REJETER')}
                        className="px-3 py-1.5 rounded-xl bg-rose-600 hover:bg-rose-700 text-white text-xs font-bold transition-colors flex items-center gap-1"
                      >
                        <X className="w-3.5 h-3.5" /> Rejeter
                      </button>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}
