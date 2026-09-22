'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import { transportAPI } from '@/lib/api-client';
import { UserPlus, Search, Phone, FileText, CheckCircle2, ShieldAlert } from 'lucide-react';
import { ModuleLayout } from '@/components/layout/ModuleLayout';
import { CardSkeletonLoader } from '@/components/ui/Loaders';
import { EmptyStates } from '@/components/design-system/EmptyState';
import { Button } from '@/components/design-system/Button';
import { Input } from '@/components/design-system/Input';

export default function DriversListPage() {
  const router = useRouter();
  const [searchTerm, setSearchTerm] = useState('');

  const { data: rawChauffeurs = [], isLoading: loading } = useQuery({
    queryKey: ['chauffeurs'],
    queryFn: async () => {
      const res = await transportAPI.getChauffeurs();
      const d = res.data;
      return Array.isArray(d) ? d : (d?.items || (Array.isArray(res) ? res : []));
    }
  });

  const chauffeurs = Array.isArray(rawChauffeurs) ? rawChauffeurs : (rawChauffeurs?.items || []);

  const filteredChauffeurs = chauffeurs.filter((c: any) => 
    c?.nom?.toLowerCase().includes(searchTerm.toLowerCase()) || 
    c?.prenom?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    c?.numero_permis?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <ModuleLayout module="transport">
      <div className="bg-slate-50 min-h-full p-4 md:p-6 lg:p-8 max-w-[1600px] mx-auto animate-in fade-in duration-500">
        
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-end justify-between mb-8 gap-4">
          <div>
            <h2 className="text-3xl font-bold tracking-tight text-slate-900 flex items-center gap-2">
              <span className="material-symbols-outlined text-[32px] text-blue-600">badge</span>
              Annuaire Chauffeurs
            </h2>
            <p className="text-sm text-slate-500 mt-1">Gérez le profil et les documents des conducteurs de la flotte</p>
          </div>
          <div className="flex items-center gap-4">
            <div className="relative">
              <Search className="w-5 h-5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <Input
                type="text"
                placeholder="Rechercher un chauffeur..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 w-64"
              />
            </div>
            <Button
              onClick={() => router.push('/transport/drivers/new')}
              className="flex items-center gap-2"
            >
              <UserPlus className="w-5 h-5" />
              Nouveau Chauffeur
            </Button>
          </div>
        </div>

        {/* Content */}
        <div className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
          <table className="w-full text-left border-collapse">
            <thead className="bg-slate-50/80 border-b border-slate-100 text-xs uppercase font-bold text-slate-500">
              <tr>
                <th className="px-6 py-4">Nom Complet</th>
                <th className="px-6 py-4">Contact</th>
                <th className="px-6 py-4">Permis & Cat.</th>
                <th className="px-6 py-4">Spécialisation</th>
                <th className="px-6 py-4">Statut</th>
                <th className="px-6 py-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr><td colSpan={6} className="px-6 py-12"><CardSkeletonLoader /></td></tr>
              ) : filteredChauffeurs.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-8">
                    <EmptyStates.NoResults
                      description={searchTerm
                        ? "Aucun chauffeur ne correspond à votre recherche."
                        : "Aucun chauffeur enregistré pour le moment."}
                      action={searchTerm ? {
                        label: 'Effacer la recherche',
                        onClick: () => setSearchTerm('')
                      } : {
                        label: 'Créer un chauffeur',
                        onClick: () => router.push('/transport/drivers/new')
                      }}
                    />
                  </td>
                </tr>
              ) : (
                filteredChauffeurs.map((chauffeur: any) => (
                  <tr key={chauffeur.id} className="hover:bg-slate-50/50 transition-colors group">
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center font-bold">
                          {chauffeur.prenom?.[0]}{chauffeur.nom?.[0]}
                        </div>
                        <div>
                          <p className="text-sm font-bold text-slate-900 group-hover:text-blue-600 transition-colors">
                            {chauffeur.prenom} {chauffeur.nom}
                          </p>
                          <p className="text-xs text-slate-500">ID: DRV-{chauffeur.id.toString().padStart(4, '0')}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-1.5 text-sm text-slate-600">
                        <Phone className="w-4 h-4 text-slate-400" />
                        {chauffeur.telephone}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm font-mono text-slate-700">{chauffeur.numero_permis}</div>
                      <div className="text-xs text-slate-500 font-medium">Cat: {chauffeur.categorie_permis}</div>
                    </td>
                    <td className="px-6 py-4">
                      <span className="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-medium bg-slate-100 text-slate-700">
                        {chauffeur.specialisation || 'Aucune'}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      {chauffeur.actif ? (
                        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold bg-emerald-50 text-emerald-700">
                          <CheckCircle2 className="w-3.5 h-3.5" /> Actif
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold bg-red-50 text-red-700">
                          <ShieldAlert className="w-3.5 h-3.5" /> Inactif
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <Button
                        variant="ghost"
                        size="sm"
                        className="p-2"
                        title="Voir profil"
                      >
                        <FileText className="w-5 h-5" />
                      </Button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </ModuleLayout>
  );
}
