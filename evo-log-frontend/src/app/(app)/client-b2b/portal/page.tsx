'use client';

import React, { useState, useEffect } from 'react';
import { 
  Globe, 
  Plus, 
  Search, 
  Filter, 
  UserCheck, 
  Key, 
  Lock, 
  Mail, 
  ShieldCheck, 
  RefreshCw,
  Building2,
  ExternalLink
} from 'lucide-react';
import { toast } from 'sonner';

interface B2BPortalUser {
  id: string;
  nomEntreprise: string;
  contactEmail: string;
  nomContact: string;
  statut: 'ACTIF' | 'EN_ATTENTE_ACTIVATION' | 'SUSPENDU';
  dossiersSuivis: number;
  dateInvitation: string;
  dernierAcces: string;
}

export default function ClientB2bPortalPage() {
  const [portalUsers, setPortalUsers] = useState<B2BPortalUser[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [showInviteModal, setShowInviteModal] = useState(false);

  const [inviteForm, setInviteForm] = useState({
    nomEntreprise: '',
    nomContact: '',
    contactEmail: '',
    autoriserTelechargementBl: true,
    autoriserDepotReclamations: true
  });

  const handleInviteSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inviteForm.nomEntreprise || !inviteForm.contactEmail) {
      toast.error('Veuillez renseigner la raison sociale et l\'email du contact.');
      return;
    }

    toast.error("L'invitation au portail B2B n'est pas encore raccordée à l'API.");
    setShowInviteModal(false);
    setInviteForm({
      nomEntreprise: '',
      nomContact: '',
      contactEmail: '',
      autoriserTelechargementBl: true,
      autoriserDepotReclamations: true
    });
    toast.error("L'activation des accès portail n'est pas encore raccordée à l'API.");
  };

  const filteredUsers = portalUsers.filter(u => 
    u.nomEntreprise.toLowerCase().includes(searchTerm.toLowerCase()) ||
    u.contactEmail.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-outline pb-5">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-primary/10 rounded-xl text-primary">
            <Globe className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-on-surface">Gestion des Accès Portail Client B2B</h1>
            <p className="text-sm text-on-surface-variant">
              Espace extranet sécurisé pour le suivi des expéditions, factures et e-PODs par vos clients
            </p>
          </div>
        </div>

        <button
          onClick={() => setShowInviteModal(true)}
          className="flex items-center gap-2 px-4 py-2 text-xs font-semibold rounded-xl bg-primary text-on-primary hover:opacity-95 transition-opacity"
        >
          <Plus className="w-4 h-4" />
          Inviter un Client B2B
        </button>
      </div>

      {/* Filter Bar */}
      <div className="bg-surface border border-outline rounded-2xl p-4 flex flex-wrap items-center justify-between gap-4">
        <div className="relative flex-1 min-w-[240px]">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant" />
          <input
            type="text"
            placeholder="Rechercher un client autorisé..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-4 py-2 bg-surface-container-low border border-outline text-xs rounded-xl text-on-surface focus:outline-none focus:border-primary"
          />
        </div>
      </div>

      {/* Table / Clean Slate State */}
      <div className="bg-surface border border-outline rounded-2xl overflow-hidden shadow-sm">
        {filteredUsers.length === 0 ? (
          <div className="p-12 text-center">
            <Globe className="w-12 h-12 text-on-surface-variant/40 mx-auto mb-3" />
            <h3 className="font-semibold text-on-surface text-base">Aucun compte client portail configuré</h3>
            <p className="text-xs text-on-surface-variant mt-1 max-w-md mx-auto mb-4">
              Donnez à vos clients chargeurs un accès direct à leur portail en libre-service pour qu'ils puissent suivre leurs conteneurs et télécharger leurs factures sans solliciter vos équipes.
            </p>
            <button
              onClick={() => setShowInviteModal(true)}
              className="px-4 py-2 bg-primary text-on-primary rounded-xl font-bold text-xs hover:opacity-95"
            >
              + Inviter le Premier Client
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="bg-surface-container-low border-b border-outline uppercase font-semibold text-on-surface-variant">
                  <th className="p-3 pl-5">Client / Raison Sociale</th>
                  <th className="p-3">Contact Titulaire</th>
                  <th className="p-3">Email de Connexion</th>
                  <th className="p-3 text-center">Dossiers Visibles</th>
                  <th className="p-3">Dernier Accès</th>
                  <th className="p-3">Statut</th>
                  <th className="p-3 text-right pr-5">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-outline/40">
                {filteredUsers.map(u => (
                  <tr key={u.id} className="hover:bg-surface-container transition-colors">
                    <td className="p-3 pl-5 font-bold text-on-surface">{u.nomEntreprise}</td>
                    <td className="p-3 text-on-surface">{u.nomContact}</td>
                    <td className="p-3 font-mono text-primary">{u.contactEmail}</td>
                    <td className="p-3 text-center font-mono font-bold text-on-surface">{u.dossiersSuivis}</td>
                    <td className="p-3 text-on-surface-variant">{u.dernierAcces}</td>
                    <td className="p-3">
                      <span className="px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-600 font-bold text-[10px]">
                        {u.statut}
                      </span>
                    </td>
                    <td className="p-3 text-right pr-5">
                      <button
                        onClick={() => toast.error("L'envoi des liens de réinitialisation n'est pas encore raccordé à l'API.")}
                        className="text-xs font-semibold text-primary hover:underline"
                      >
                        Renvoyer Accès
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Invite Modal */}
      {showInviteModal && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-surface border border-outline rounded-2xl w-full max-w-md p-6 space-y-4 shadow-xl">
            <div className="flex justify-between items-center border-b border-outline pb-3">
              <h3 className="font-bold text-on-surface text-base">Activer un Accès Portail Client</h3>
              <button onClick={() => setShowInviteModal(false)} className="text-on-surface-variant hover:text-on-surface">✕</button>
            </div>

            <form onSubmit={handleInviteSubmit} className="space-y-3 text-xs">
              <div>
                <label className="block text-on-surface-variant font-medium mb-1">Raison Sociale du Client * :</label>
                <input
                  type="text"
                  placeholder="Ex: CABCEM Industries SA"
                  value={inviteForm.nomEntreprise}
                  onChange={(e) => setInviteForm({ ...inviteForm, nomEntreprise: e.target.value })}
                  required
                  className="w-full p-2 bg-surface-container-low border border-outline rounded-xl text-on-surface font-semibold focus:outline-none focus:border-primary"
                />
              </div>

              <div>
                <label className="block text-on-surface-variant font-medium mb-1">Nom & Prénom du Responsable :</label>
                <input
                  type="text"
                  placeholder="Ex: Jean-Marc Eboa"
                  value={inviteForm.nomContact}
                  onChange={(e) => setInviteForm({ ...inviteForm, nomContact: e.target.value })}
                  className="w-full p-2 bg-surface-container-low border border-outline rounded-xl text-on-surface focus:outline-none focus:border-primary"
                />
              </div>

              <div>
                <label className="block text-on-surface-variant font-medium mb-1">Email Professionnel (Identifiant) * :</label>
                <input
                  type="email"
                  placeholder="logistique@client.cm"
                  value={inviteForm.contactEmail}
                  onChange={(e) => setInviteForm({ ...inviteForm, contactEmail: e.target.value })}
                  required
                  className="w-full p-2 bg-surface-container-low border border-outline rounded-xl text-on-surface focus:outline-none focus:border-primary"
                />
              </div>

              <div className="pt-2 space-y-2">
                <label className="flex items-center gap-2 text-xs text-on-surface cursor-pointer">
                  <input
                    type="checkbox"
                    checked={inviteForm.autoriserTelechargementBl}
                    onChange={(e) => setInviteForm({ ...inviteForm, autoriserTelechargementBl: e.target.checked })}
                    className="rounded text-primary focus:ring-primary"
                  />
                  <span>Autoriser le téléchargement des Bons à Délivrer (BL) et e-PODs</span>
                </label>

                <label className="flex items-center gap-2 text-xs text-on-surface cursor-pointer">
                  <input
                    type="checkbox"
                    checked={inviteForm.autoriserDepotReclamations}
                    onChange={(e) => setInviteForm({ ...inviteForm, autoriserDepotReclamations: e.target.checked })}
                    className="rounded text-primary focus:ring-primary"
                  />
                  <span>Autoriser l'ouverture directe de réclamations et litiges</span>
                </label>
              </div>

              <div className="pt-3 flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setShowInviteModal(false)}
                  className="px-4 py-2 border border-outline rounded-xl text-on-surface hover:bg-surface-container font-semibold"
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-primary text-on-primary rounded-xl font-bold hover:opacity-90"
                >
                  Générer Accès Sécurisé
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
