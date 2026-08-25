'use client'

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { transportAPI } from '@/lib/api-client';
import { UserPlus, User, Phone, MapPin, Truck, AlertCircle, CheckCircle2 } from 'lucide-react';
import ModuleLayout from '@/components/layout/ModuleLayout';

export default function NewDriverPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    nom: '',
    prenom: '',
    telephone: '',
    adresse: '',
    contact_urgence_nom: '',
    contact_urgence_telephone: '',
    numero_permis: '',
    categorie_permis: '',
    specialisation: ''
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      await transportAPI.createChauffeur(formData);
      setSuccess('Le profil chauffeur a Ã©tÃ© crÃ©Ã© avec succÃ¨s.');
      // Optional: redirect to drivers list after a short delay
      setTimeout(() => {
        router.push('/transport/control'); // Or a drivers list page if it exists
      }, 2000);
    } catch (err: any) {
      console.error(err);
      setError(err.response?.data?.detail || 'Une erreur est survenue lors de la crÃ©ation du profil.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ModuleLayout module="transport">
      <div className="max-w-4xl mx-auto py-8 px-4 sm:px-6 lg:px-8 animate-in fade-in duration-500">
        
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-900 flex items-center gap-3">
            <UserPlus className="w-8 h-8 text-blue-600" />
            Nouveau Chauffeur
          </h1>
          <p className="text-slate-500 mt-2">
            Enregistrez un nouveau conducteur dans la flotte EVO-Transport.
          </p>
        </div>

        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-xl p-4 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-600 mt-0.5" />
            <div className="flex-1">
              <h3 className="text-sm font-semibold text-red-800">Erreur de crÃ©ation</h3>
              <p className="text-sm text-red-600 mt-1">{error}</p>
            </div>
          </div>
        )}

        {success && (
          <div className="mb-6 bg-green-50 border border-green-200 rounded-xl p-4 flex items-start gap-3">
            <CheckCircle2 className="w-5 h-5 text-green-600 mt-0.5" />
            <div className="flex-1">
              <h3 className="text-sm font-semibold text-green-800">SuccÃ¨s</h3>
              <p className="text-sm text-green-600 mt-1">{success}</p>
            </div>
          </div>
        )}

        <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
          <form onSubmit={handleSubmit} className="divide-y divide-slate-100">
            
            {/* Bloc "IdentitÃ© & Contact" */}
            <div className="p-6 md:p-8">
              <div className="flex items-center gap-2 mb-6">
                <div className="p-2 bg-blue-50 rounded-lg text-blue-600">
                  <User className="w-5 h-5" />
                </div>
                <h2 className="text-lg font-semibold text-slate-800">IdentitÃ© & Contact</h2>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1.5">Nom *</label>
                  <input
                    type="text"
                    name="nom"
                    required
                    value={formData.nom}
                    onChange={handleChange}
                    className="w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all"
                    placeholder="Ex: Ndiaye"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1.5">PrÃ©nom *</label>
                  <input
                    type="text"
                    name="prenom"
                    required
                    value={formData.prenom}
                    onChange={handleChange}
                    className="w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all"
                    placeholder="Ex: Amadou"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1.5">TÃ©lÃ©phone *</label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <Phone className="w-4 h-4 text-slate-400" />
                    </div>
                    <input
                      type="tel"
                      name="telephone"
                      required
                      value={formData.telephone}
                      onChange={handleChange}
                      className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all"
                      placeholder="+237 ..."
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1.5">Adresse</label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <MapPin className="w-4 h-4 text-slate-400" />
                    </div>
                    <input
                      type="text"
                      name="adresse"
                      value={formData.adresse}
                      onChange={handleChange}
                      className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all"
                      placeholder="Lieu de rÃ©sidence"
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* Bloc "Contact d'Urgence" */}
            <div className="p-6 md:p-8 bg-slate-50/50">
              <h2 className="text-sm font-bold text-slate-500 uppercase tracking-wider mb-6">Contact d'Urgence</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1.5">Nom du contact</label>
                  <input
                    type="text"
                    name="contact_urgence_nom"
                    value={formData.contact_urgence_nom}
                    onChange={handleChange}
                    className="w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all bg-white"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1.5">TÃ©lÃ©phone d'urgence</label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <Phone className="w-4 h-4 text-slate-400" />
                    </div>
                    <input
                      type="tel"
                      name="contact_urgence_telephone"
                      value={formData.contact_urgence_telephone}
                      onChange={handleChange}
                      className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all bg-white"
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* Bloc "ConformitÃ© LÃ©gale & OpÃ©rationnelle" */}
            <div className="p-6 md:p-8">
              <div className="flex items-center gap-2 mb-6">
                <div className="p-2 bg-amber-50 rounded-lg text-amber-600">
                  <Truck className="w-5 h-5" />
                </div>
                <h2 className="text-lg font-semibold text-slate-800">ConformitÃ© LÃ©gale & CompÃ©tences</h2>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1.5">NÂ° de Permis *</label>
                  <input
                    type="text"
                    name="numero_permis"
                    required
                    value={formData.numero_permis}
                    onChange={handleChange}
                    className="w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all font-mono"
                    placeholder="XXXX-XXXX"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1.5">CatÃ©gorie *</label>
                  <select
                    name="categorie_permis"
                    required
                    value={formData.categorie_permis}
                    onChange={handleChange}
                    className="w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all bg-white"
                  >
                    <option value="">SÃ©lectionner</option>
                    <option value="B">B (LÃ©ger)</option>
                    <option value="C">C (Lourd)</option>
                    <option value="CE">CE (Super Lourd / Semi)</option>
                    <option value="D">D (Transport commun)</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1.5">SpÃ©cialisation</label>
                  <select
                    name="specialisation"
                    value={formData.specialisation}
                    onChange={handleChange}
                    className="w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all bg-white"
                  >
                    <option value="">Aucune spÃ©cifique</option>
                    <option value="MATIERES_DANGEREUSES">MatiÃ¨res Dangereuses (ADR)</option>
                    <option value="CONDUITE_URBAINE">Conduite Urbaine</option>
                    <option value="PORTE_CONTENEURS">Porte-conteneurs spÃ©cifiques</option>
                    <option value="CONVOI_EXCEPTIONNEL">Convoi Exceptionnel</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="p-6 bg-slate-50 flex items-center justify-end gap-4">
              <button
                type="button"
                onClick={() => router.back()}
                className="px-6 py-2.5 rounded-xl font-medium text-slate-600 hover:bg-slate-200/50 transition-colors"
                disabled={loading}
              >
                Annuler
              </button>
              <button
                type="submit"
                disabled={loading}
                className="px-8 py-2.5 rounded-xl font-medium text-white bg-blue-600 hover:bg-blue-700 focus:ring-4 focus:ring-blue-500/20 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 shadow-sm"
              >
                {loading ? (
                  <>
                    <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    CrÃ©ation...
                  </>
                ) : (
                  <>
                    <UserPlus className="w-5 h-5" />
                    Enregistrer le chauffeur
                  </>
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </ModuleLayout>
  );
}
