'use client';

import React, { useState, useEffect } from 'react';
import { ModuleLayout } from '@/components/layout/ModuleLayout';
import { Badge, CalendarDays, FileText, UserCircle, Briefcase, Plus, Send } from 'lucide-react';
import { rhAPI } from '@/lib/api-client';
import { toast } from 'sonner';

export default function MonEspaceRHPage() {
  const [profile, setProfile] = useState<any>(null);
  const [conges, setConges] = useState<any[]>([]);
  const [paies, setPaies] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCongeModal, setShowCongeModal] = useState(false);
  const [congeData, setCongeData] = useState({ type_conge: 'ANNUEL', date_debut: '', date_fin: '', motif: '' });

  useEffect(() => {
    loadProfileAndData();
  }, []);

  const loadProfileAndData = async () => {
    try {
      setLoading(true);
      const profileRes = await rhAPI.getMyProfile();
      const userProfile = profileRes.data;
      setProfile(userProfile);

      if (userProfile) {
        const [congesRes, paiesRes] = await Promise.all([
          rhAPI.getConges().catch(() => ({ data: [] })),
          rhAPI.getPaie().catch(() => ({ data: [] }))
        ]);
        
        // Filter by logged-in employee ID safely
        const rawConges = Array.isArray(congesRes.data) ? congesRes.data : (congesRes.data?.items || (Array.isArray(congesRes) ? congesRes : []));
        const rawPaies = Array.isArray(paiesRes.data) ? paiesRes.data : (paiesRes.data?.items || (Array.isArray(paiesRes) ? paiesRes : []));
        const myConges = rawConges.filter((c: any) => c.employe_id === userProfile.id);
        const myPaies = rawPaies.filter((p: any) => p.employe_id === userProfile.id);
        
        setConges(myConges);
        setPaies(myPaies);
      }
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || "Erreur lors du chargement de l'espace personnel");
      setConges([]);
      setPaies([]);
    } finally {
      setLoading(false);
    }
  };

  const submitConge = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!profile) return;
    try {
      await rhAPI.createConge({ ...congeData, employe_id: profile.id });
      toast.success("Demande de congé envoyée");
      setShowCongeModal(false);
      setCongeData({ type_conge: 'ANNUEL', date_debut: '', date_fin: '', motif: '' });
      loadProfileAndData();
    } catch (e) {
      toast.error("Erreur lors de la soumission");
    }
  };

  if (loading) return <ModuleLayout module="rh"><div className="p-8 text-center text-slate-500">Chargement de votre espace...</div></ModuleLayout>;
  if (!profile) return <ModuleLayout module="rh"><div className="p-8 text-center text-red-500 font-bold">Profil employé non configuré. Veuillez contacter un administrateur pour lier votre compte utilisateur à un profil employé.</div></ModuleLayout>;

  return (
    <ModuleLayout module="rh">
      <div className="max-w-7xl mx-auto py-8 px-4">
        {/* En-tête du profil */}
        <div className="bg-white rounded-3xl p-8 shadow-sm border border-slate-200 mb-8 flex flex-col md:flex-row items-center gap-6">
          <div className="h-24 w-24 rounded-full bg-teal-100 flex items-center justify-center text-teal-600">
            <UserCircle className="h-16 w-16" />
          </div>
          <div className="flex-1 text-center md:text-left">
            <h1 className="text-3xl font-black text-slate-800">{profile?.prenom} {profile?.nom}</h1>
            <p className="text-lg text-slate-500 font-medium">{profile?.poste} • {profile?.departement}</p>
            <div className="flex flex-wrap gap-3 mt-4 justify-center md:justify-start">
              <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-slate-100 text-slate-600 rounded-lg text-sm font-bold">
                <Badge className="w-4 h-4" /> {profile?.matricule}
              </span>
              <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-emerald-50 text-emerald-600 rounded-lg text-sm font-bold">
                <Briefcase className="w-4 h-4" /> {profile?.statut}
              </span>
            </div>
          </div>
          <div className="flex gap-3">
            <button 
              onClick={() => setShowCongeModal(true)}
              className="px-6 py-3 bg-teal-600 text-white rounded-xl font-bold flex items-center gap-2 hover:bg-teal-700 transition-colors shadow-lg shadow-teal-200"
            >
              <CalendarDays className="w-5 h-5" />
              Demander un Congé
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Fiches de paie */}
          <div className="bg-white rounded-3xl p-6 shadow-sm border border-slate-200">
            <div className="flex items-center gap-3 mb-6">
              <FileText className="w-6 h-6 text-teal-600" />
              <h2 className="text-xl font-bold text-slate-800">Mes Fiches de Paie</h2>
            </div>
            <div className="space-y-4">
              {paies.length === 0 ? (
                <p className="text-sm text-slate-500 py-4 text-center">Aucune fiche de paie générée.</p>
              ) : (
                paies.map((p, idx) => (
                  <div key={p.id || idx} className="p-4 rounded-xl border border-slate-100 hover:border-teal-200 bg-slate-50 transition-colors flex justify-between items-center">
                    <div>
                      <p className="font-bold text-slate-700">Période : {p.periode}</p>
                      <p className="text-sm text-slate-500">Net à payer : {Number(p.net_a_payer).toLocaleString()} FCFA</p>
                    </div>
                    <button className="text-teal-600 font-bold hover:underline text-sm">Visualiser</button>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Mes Absences / Congés */}
          <div className="bg-white rounded-3xl p-6 shadow-sm border border-slate-200">
            <div className="flex items-center gap-3 mb-6">
              <CalendarDays className="w-6 h-6 text-amber-500" />
              <h2 className="text-xl font-bold text-slate-800">Historique des Absences</h2>
            </div>
            <div className="space-y-4">
              {conges.length === 0 ? (
                <p className="text-sm text-slate-500 py-4 text-center">Aucune demande de congé enregistrée.</p>
              ) : (
                conges.map((c, idx) => (
                  <div key={c.id || idx} className="p-4 rounded-xl border border-slate-100 bg-white shadow-sm flex flex-col gap-2">
                    <div className="flex justify-between items-start">
                      <span className="font-bold text-slate-700">Congé {c.type_conge}</span>
                      <span className={`px-2 py-1 text-xs font-bold rounded ${
                        c.statut === 'APPROUVE' ? 'bg-emerald-100 text-emerald-700' :
                        c.statut === 'REFUSE' ? 'bg-rose-100 text-rose-700' : 'bg-slate-100 text-slate-700'
                      }`}>{c.statut}</span>
                    </div>
                    <p className="text-sm text-slate-500">Du {new Date(c.date_debut).toLocaleDateString()} au {new Date(c.date_fin).toLocaleDateString()}</p>
                    {c.motif && <p className="text-xs italic text-slate-400">Motif : {c.motif}</p>}
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Modal Demande Congé */}
        {showCongeModal && (
          <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <div className="bg-white rounded-3xl p-8 max-w-md w-full animate-in zoom-in-95">
              <h2 className="text-2xl font-black text-slate-800 mb-6 flex items-center gap-2">
                <CalendarDays className="text-teal-600" /> Nouvelle demande
              </h2>
              <form onSubmit={submitConge} className="space-y-4">
                <div>
                  <label className="block text-sm font-bold text-slate-700 mb-2">Type d'absence</label>
                  <select value={congeData.type_conge} onChange={e => setCongeData({...congeData, type_conge: e.target.value})} className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 outline-none focus:border-teal-500">
                    <option value="ANNUEL">Congé Annuel</option>
                    <option value="MALADIE">Congé Maladie</option>
                    <option value="MATERNITE">Congé Maternité/Paternité</option>
                    <option value="SANS_SOLDE">Sans Solde</option>
                  </select>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-bold text-slate-700 mb-2">Date début</label>
                    <input type="date" required value={congeData.date_debut} onChange={e => setCongeData({...congeData, date_debut: e.target.value})} className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 outline-none focus:border-teal-500"/>
                  </div>
                  <div>
                    <label className="block text-sm font-bold text-slate-700 mb-2">Date fin</label>
                    <input type="date" required value={congeData.date_fin} onChange={e => setCongeData({...congeData, date_fin: e.target.value})} className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 outline-none focus:border-teal-500"/>
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-bold text-slate-700 mb-2">Motif (Optionnel)</label>
                  <textarea value={congeData.motif} onChange={e => setCongeData({...congeData, motif: e.target.value})} className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 outline-none focus:border-teal-500 h-24" placeholder="Précisez la raison si nécessaire..."/>
                </div>
                <div className="flex gap-4 pt-4">
                  <button type="button" onClick={() => setShowCongeModal(false)} className="flex-1 py-3 bg-slate-100 text-slate-700 font-bold rounded-xl hover:bg-slate-200">Annuler</button>
                  <button type="submit" className="flex-1 py-3 bg-teal-600 text-white font-bold rounded-xl hover:bg-teal-700 flex justify-center items-center gap-2">
                    <Send className="w-4 h-4" /> Envoyer
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </ModuleLayout>
  );
}
