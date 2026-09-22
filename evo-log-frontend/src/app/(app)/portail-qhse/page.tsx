'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  ShieldAlert, CheckCircle2, Clock, AlertTriangle, RefreshCw,
  Camera, ShieldCheck, HeartPulse, FileText, Search, PlusCircle,
  Activity, AlertOctagon, HelpCircle, Check, Award
} from 'lucide-react';
import { qhseAPI } from '@/lib/api-client';
import { toast } from 'sonner';

interface IncidentItem {
  id: number;
  titre: string;
  type_incident: string;
  severite: string;
  lieu: string;
  date_incident?: string;
  statut: string;
  description?: string;
}

export default function PortailQHSEPage() {
  const [activeTab, setActiveTab] = useState<'flash' | 'checklists' | 'fds' | 'statistiques'>('flash');
  const [incidents, setIncidents] = useState<IncidentItem[]>([]);
  const [loading, setLoading] = useState(true);

  // Formulaire Flash Danger
  const [flashForm, setFlashForm] = useState({
    titre: 'Fuite d’huile sur dalle quai n°3',
    type_incident: 'SITUATION_DANGEREUSE',
    severite: 'MOYENNE',
    lieu: 'Entrepôt Central - Quai 3',
    description: 'Flaque d’huile moteur risquant de causer des dérapages de chariots élévateurs ou des chutes de piétons.',
  });
  const [submittingFlash, setSubmittingFlash] = useState(false);

  // Checklist EPI
  const [epiChecklist, setEpiChecklist] = useState({
    chaussures_securite: true,
    gilet_haute_visibilite: true,
    casque_chantier: true,
    gants_manutention: true,
    lunettes_protection: false,
    harnais_anti_chute: false,
  });

  // FDS search
  const [fdsSearch, setFdsSearch] = useState('');
  const fdsList = [
    { code: 'UN 1203', nom: 'ESSENCE / CARBURANT AUTO', classe: 'Classe 3 - Liquides Inflammables', consignes: 'Éloigner toute flamme, ventiler la zone, utiliser extincteur poudre ABC.' },
    { code: 'UN 1202', nom: 'GAZOLE / DIESEL', classe: 'Classe 3 - Liquides Inflammables', consignes: 'Absorber avec du sable ou absorbant végétal, ne pas rejeter dans les égouts.' },
    { code: 'UN 1978', nom: 'PROPANE / GAZ HYDROCARBURE', classe: 'Classe 2.1 - Gaz Inflammables', consignes: 'Évacuer la zone sous le vent, couper les sources d’ignition, arroser les récipients.' },
    { code: 'UN 1824', nom: 'HYDROXYDE DE SODIUM EN SOLUTION', classe: 'Classe 8 - Matières Corrosives', consignes: 'Port obligatoire de gants néoprène et visière de protection. Rincer abondamment à l’eau claire.' },
  ];

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const res = await qhseAPI.getIncidents();
      const list = Array.isArray(res.data) ? res.data : (res.data?.items || []);
      setIncidents(list);
    } catch (err: any) {
      toast.error('Erreur chargement données QHSE');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleCreateFlash = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmittingFlash(true);
    try {
      await qhseAPI.createIncident({
        ...flashForm,
      });
      toast.success('Signalement de sécurité transmis à la vigie QHSE !');
      setFlashForm({
        titre: '',
        type_incident: 'SITUATION_DANGEREUSE',
        severite: 'MOYENNE',
        lieu: '',
        description: '',
      });
      fetchData();
      setActiveTab('statistiques');
    } catch (err: any) {
      toast.error('Erreur lors du signalement');
    } finally {
      setSubmittingFlash(false);
    }
  };

  const filteredFds = fdsList.filter(f =>
    f.nom.toLowerCase().includes(fdsSearch.toLowerCase()) ||
    f.code.toLowerCase().includes(fdsSearch.toLowerCase()) ||
    f.classe.toLowerCase().includes(fdsSearch.toLowerCase())
  );

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="bg-gradient-to-r from-slate-900 via-rose-950 to-slate-900 rounded-3xl p-6 sm:p-8 text-white border border-rose-900/40 shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="space-y-2">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-rose-500/20 text-rose-400 border border-rose-500/30 text-xs font-bold uppercase tracking-wider">
            <ShieldAlert className="w-3.5 h-3.5" /> Portail Vigie Sécurité & QHSE
          </div>
          <h1 className="text-2xl sm:text-3xl font-black tracking-tight">
            Espace Sécurité Terrain & Prévention
          </h1>
          <p className="text-sm text-slate-300">
            Signalez une situation dangereuse en 30 secondes, contrôlez vos EPI et consultez les fiches de sécurité.
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

      {/* Tabs */}
      <div className="flex overflow-x-auto gap-2 p-1.5 bg-slate-100 rounded-2xl border border-slate-200">
        {[
          { id: 'flash', label: 'Signalement Flash Danger (30s)', icon: AlertTriangle },
          { id: 'checklists', label: 'Contrôle Port des EPI', icon: ShieldCheck },
          { id: 'fds', label: 'Matières Dangereuses (FDS / IMDG)', icon: FileText },
          { id: 'statistiques', label: 'Historique & Jours Sans Accident', icon: Award, count: incidents.length },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-2 px-4 py-3 rounded-xl text-xs sm:text-sm font-bold whitespace-nowrap transition-all ${
                isActive
                  ? 'bg-white text-slate-900 shadow-md border border-slate-200'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-white/50'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{tab.label}</span>
              {tab.count !== undefined && (
                <span className={`px-2 py-0.5 rounded-full text-[11px] font-mono ${
                  isActive ? 'bg-slate-900 text-white' : 'bg-slate-200 text-slate-700'
                }`}>
                  {tab.count}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Onglet 1 : Signalement Flash */}
      {activeTab === 'flash' && (
        <div className="bg-white rounded-2xl border border-slate-200 p-6 space-y-6 max-w-2xl mx-auto shadow-sm">
          <div className="pb-4 border-b border-slate-100">
            <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-rose-600" /> Remontée Flash d'un Danger ou Presqu'Accident
            </h2>
            <p className="text-xs text-slate-500">
              Contribuez à sauver des vies : signalez tout risque identifié dans votre journée.
            </p>
          </div>

          <form onSubmit={handleCreateFlash} className="space-y-4">
            <div>
              <label className="text-xs font-bold text-slate-700 block mb-1">Titre Court de la Situation</label>
              <input
                type="text"
                required
                value={flashForm.titre}
                onChange={(e) => setFlashForm({ ...flashForm, titre: e.target.value })}
                className="w-full px-3 py-2 rounded-xl border border-slate-300 text-xs focus:ring-2 focus:ring-rose-500 outline-none"
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="text-xs font-bold text-slate-700 block mb-1">Type de Signalement</label>
                <select
                  value={flashForm.type_incident}
                  onChange={(e) => setFlashForm({ ...flashForm, type_incident: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl border border-slate-300 text-xs focus:ring-2 focus:ring-rose-500 outline-none"
                >
                  <option value="SITUATION_DANGEREUSE">Situation Dangereuse (Obstacle, Fuite)</option>
                  <option value="PRESQU_ACCIDENT">Presqu'Accident (Near-Miss évité de justesse)</option>
                  <option value="NON_CONFORMITE_EPI">Non-respect du port des EPI</option>
                  <option value="POLLUTION_ENVIRONNEMENT">Fuite produit polluant / Carburant</option>
                  <option value="DEGRADATION_MATERIEL">Dégradation équipement de sécurité</option>
                </select>
              </div>

              <div>
                <label className="text-xs font-bold text-slate-700 block mb-1">Degré de Gravité</label>
                <select
                  value={flashForm.severite}
                  onChange={(e) => setFlashForm({ ...flashForm, severite: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl border border-slate-300 text-xs focus:ring-2 focus:ring-rose-500 outline-none font-bold"
                >
                  <option value="BASSE">Faible (Risque mineur)</option>
                  <option value="MOYENNE">Moyenne (Action requise sous 24h)</option>
                  <option value="HAUTE">Haute (Danger sérieux)</option>
                  <option value="CRITIQUE">Critique (Arrêt immédiat requis)</option>
                </select>
              </div>
            </div>

            <div>
              <label className="text-xs font-bold text-slate-700 block mb-1">Lieu Exact / Quai / Entrepôt</label>
              <input
                type="text"
                required
                value={flashForm.lieu}
                onChange={(e) => setFlashForm({ ...flashForm, lieu: e.target.value })}
                className="w-full px-3 py-2 rounded-xl border border-slate-300 text-xs focus:ring-2 focus:ring-rose-500 outline-none"
              />
            </div>

            <div>
              <label className="text-xs font-bold text-slate-700 block mb-1">Description / Constats</label>
              <textarea
                rows={3}
                value={flashForm.description}
                onChange={(e) => setFlashForm({ ...flashForm, description: e.target.value })}
                className="w-full px-3 py-2 rounded-xl border border-slate-300 text-xs focus:ring-2 focus:ring-rose-500 outline-none"
              />
            </div>

            <button
              type="submit"
              disabled={submittingFlash}
              className="w-full py-3 rounded-xl bg-rose-600 hover:bg-rose-700 text-white text-xs font-black uppercase tracking-wider transition-colors shadow-sm flex items-center justify-center gap-2"
            >
              <AlertTriangle className="w-4 h-4" />
              {submittingFlash ? 'Transmission en cours...' : 'Transmettre l’alerte de sécurité'}
            </button>
          </form>
        </div>
      )}

      {/* Onglet 2 : Contrôle EPI */}
      {activeTab === 'checklists' && (
        <div className="bg-white rounded-2xl border border-slate-200 p-6 space-y-6 max-w-2xl mx-auto shadow-sm">
          <div className="pb-4 border-b border-slate-100">
            <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
              <ShieldCheck className="w-5 h-5 text-emerald-600" /> Auto-Contrôle Port des Équipements de Protection
            </h2>
            <p className="text-xs text-slate-500">
              Vérifiez la conformité de votre tenue de sécurité avant d'entrer en zone d'exploitation.
            </p>
          </div>

          <div className="space-y-3">
            {[
              { key: 'chaussures_securite', label: 'Chaussures de sécurité avec embout acier' },
              { key: 'gilet_haute_visibilite', label: 'Gilet haute visibilité rétro-réfléchissant' },
              { key: 'casque_chantier', label: 'Casque de chantier jugulaire ajustée' },
              { key: 'gants_manutention', label: 'Gants de manutention adaptés' },
              { key: 'lunettes_protection', label: 'Lunettes de protection contre les projections' },
              { key: 'harnais_anti_chute', label: 'Harnais anti-chute (si travail en hauteur)' },
            ].map((item) => (
              <label
                key={item.key}
                className={`flex items-center justify-between p-4 rounded-xl border cursor-pointer transition-all ${
                  epiChecklist[item.key as keyof typeof epiChecklist]
                    ? 'bg-emerald-50/70 border-emerald-300'
                    : 'bg-slate-50 border-slate-200'
                }`}
              >
                <div className="flex items-center gap-3">
                  <input
                    type="checkbox"
                    checked={epiChecklist[item.key as keyof typeof epiChecklist]}
                    onChange={(e) => setEpiChecklist({ ...epiChecklist, [item.key]: e.target.checked })}
                    className="rounded text-emerald-600 focus:ring-emerald-500 w-4 h-4"
                  />
                  <span className="text-xs font-bold text-slate-800">{item.label}</span>
                </div>
                <span className={`text-[10px] font-bold ${
                  epiChecklist[item.key as keyof typeof epiChecklist] ? 'text-emerald-700' : 'text-slate-400'
                }`}>
                  {epiChecklist[item.key as keyof typeof epiChecklist] ? 'Conforme' : 'Non porté'}
                </span>
              </label>
            ))}
          </div>

          <Button
            onClick={() => {
              const compliantItems = Object.values(epiChecklist).filter(v => v).length;
              const totalItems = Object.keys(epiChecklist).length;
              if (compliantItems === totalItems) {
                toast.success('EPI conformes enregistrés avec succès !');
              } else {
                toast.error(`Vérifiez vos EPI : ${compliantItems}/${totalItems} items conformes`);
              }
            }}
            className="w-full"
          >
            Valider mon port des EPI
          </Button>
        </div>
      )}

      {/* Onglet 3 : Fiches FDS / IMDG */}
      {activeTab === 'fds' && (
        <div className="bg-white rounded-2xl border border-slate-200 p-6 space-y-6 shadow-sm">
          <div className="pb-4 border-b border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                <FileText className="w-5 h-5 text-indigo-600" /> Répertoire d’Urgence Fiches de Sécurité (FDS)
              </h2>
              <p className="text-xs text-slate-500">
                Consignes d’intervention immédiate en cas de fuite de matières dangereuses (Code IMDG / ADR).
              </p>
            </div>

            <div className="relative w-full sm:w-64">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
              <input
                type="text"
                placeholder="Rechercher code UN, nom..."
                value={fdsSearch}
                onChange={(e) => setFdsSearch(e.target.value)}
                className="w-full pl-9 pr-3 py-1.5 rounded-xl border border-slate-300 text-xs focus:ring-2 focus:ring-indigo-500 outline-none"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {filteredFds.map((item, idx) => (
              <div key={idx} className="p-5 rounded-2xl border border-slate-200 bg-slate-50 space-y-2">
                <div className="flex items-center justify-between gap-2">
                  <span className="font-mono text-xs font-black px-2.5 py-0.5 rounded bg-amber-100 text-amber-900">
                    {item.code}
                  </span>
                  <span className="text-[10px] font-bold text-slate-500 uppercase">{item.classe}</span>
                </div>
                <h3 className="text-sm font-bold text-slate-900">{item.nom}</h3>
                <p className="text-xs text-slate-600 leading-relaxed bg-white p-3 rounded-xl border border-slate-200/80">
                  <strong className="text-rose-700">Consignes immédiates :</strong> {item.consignes}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Onglet 4 : Statistiques & Jours Sans Accident */}
      {activeTab === 'statistiques' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="p-6 rounded-2xl bg-gradient-to-br from-emerald-500 to-teal-700 text-white shadow-md space-y-1">
              <span className="text-xs font-bold uppercase tracking-wider text-emerald-100">Sécurité Opérationnelle</span>
              <div className="text-3xl font-black">184 Jours</div>
              <p className="text-xs text-emerald-100">Consécutifs sans accident avec arrêt de travail</p>
            </div>

            <div className="p-6 rounded-2xl bg-white border border-slate-200 shadow-sm space-y-1">
              <span className="text-xs font-bold text-slate-500 uppercase">Signalements Enregistrés</span>
              <div className="text-3xl font-black text-slate-900">{incidents.length}</div>
              <p className="text-xs text-slate-500">Remontées actives dans le système</p>
            </div>

            <div className="p-6 rounded-2xl bg-white border border-slate-200 shadow-sm space-y-1">
              <span className="text-xs font-bold text-indigo-600 uppercase">Taux de Traitement</span>
              <div className="text-3xl font-black text-indigo-600">96.4 %</div>
              <p className="text-xs text-slate-500">Situations sécurisées sous 48h</p>
            </div>
          </div>

          <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm">
            <div className="p-4 border-b border-slate-100">
              <h2 className="text-sm font-bold text-slate-800 uppercase tracking-wider">
                Derniers Événements Sécurité Enregistrés ({incidents.length})
              </h2>
            </div>

            <div className="divide-y divide-slate-100">
              {incidents.length === 0 ? (
                <div className="p-8 text-center text-slate-500 text-xs">
                  Aucun incident récent signalé.
                </div>
              ) : (
                incidents.map((inc) => (
                  <div key={inc.id} className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:bg-slate-50/80">
                    <div>
                      <div className="text-xs font-bold text-slate-900">{inc.titre}</div>
                      <div className="text-[11px] text-slate-500">Lieu : {inc.lieu} • Type : {inc.type_incident}</div>
                    </div>
                    <div>
                      <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold ${
                        inc.severite === 'CRITIQUE' ? 'bg-rose-100 text-rose-800' :
                        inc.severite === 'HAUTE' ? 'bg-amber-100 text-amber-800' : 'bg-blue-100 text-blue-800'
                      }`}>
                        {inc.severite}
                      </span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
