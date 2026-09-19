'use client';

import React, { useState, useEffect } from 'react';
import {
  Users,
  Plus,
  Search,
  Shield,
  UserCheck,
  UserX,
  Mail,
  RefreshCw,
  Building,
  KeyRound,
  CheckCircle2,
  Lock
} from 'lucide-react';
import { adminAPI } from '@/lib/api-client';
import { toast } from 'sonner';

export default function UserManagementPage() {
  const [users, setUsers] = useState<any[]>([]);
  const [roles, setRoles] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [roleFilter, setRoleFilter] = useState('ALL');

  // Modal State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [newUser, setNewUser] = useState({
    username: '',
    email: '',
    full_name: '',
    password: '',
    role: 'LOGISTICIEN',
    is_active: true
  });

  const loadUsersAndRoles = async () => {
    setLoading(true);
    try {
      const [uRes, rRes] = await Promise.allSettled([
        adminAPI.getUsers(),
        adminAPI.getRoles()
      ]);

      if (uRes.status === 'fulfilled') {
        const raw = uRes.value.data?.items || uRes.value.data || [];
        setUsers(Array.isArray(raw) ? raw : []);
      }
      if (rRes.status === 'fulfilled') {
        const raw = rRes.value.data?.items || rRes.value.data || [];
        setRoles(Array.isArray(raw) ? raw : []);
      }
    } catch (err) {
      console.error('Failed to load users', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadUsersAndRoles();
  }, []);

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await adminAPI.createUser(newUser);
      toast.success(`Compte utilisateur pour ${newUser.email} créé avec succès !`);
      setIsModalOpen(false);
      setNewUser({
        username: '',
        email: '',
        full_name: '',
        password: '',
        role: 'LOGISTICIEN',
        is_active: true
      });
      loadUsersAndRoles();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Erreur lors de la création de l'utilisateur.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleToggleStatus = async (user: any) => {
    try {
      await adminAPI.toggleUserStatus(user.id);
      toast.success(`Statut de ${user.email} mis à jour.`);
      loadUsersAndRoles();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Erreur lors du changement de statut.");
    }
  };

  const handleResetPassword = async (user: any) => {
    try {
      await adminAPI.resetPassword(user.id, "EvoLog2026!");
      toast.success(`Mot de passe réinitialisé pour ${user.email} (défaut: EvoLog2026!).`);
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Erreur lors de la réinitialisation.");
    }
  };

  const filteredUsers = users.filter((u) => {
    const matchRole = roleFilter === 'ALL' || u.role === roleFilter;
    const q = searchQuery.toLowerCase();
    const matchQuery = !q || (
      (u.email && u.email.toLowerCase().includes(q)) ||
      (u.full_name && u.full_name.toLowerCase().includes(q)) ||
      (u.username && u.username.toLowerCase().includes(q))
    );
    return matchRole && matchQuery;
  });

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-outline pb-5">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-primary/10 rounded-xl text-primary">
            <Users className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-on-surface">Gestion des Utilisateurs & Accréditations</h1>
            <p className="text-sm text-on-surface-variant">
              Comptes collaborateurs, rôles hiérarchiques RBAC, habilitations par agence et sécurité des accès
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={loadUsersAndRoles}
            className="p-2 border border-outline rounded-xl text-on-surface-variant hover:bg-surface-container"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
          <button
            onClick={() => setIsModalOpen(true)}
            className="flex items-center gap-1.5 px-4 py-2 text-xs font-semibold rounded-xl bg-primary text-on-primary hover:opacity-90"
          >
            <Plus className="w-4 h-4" /> Nouvel Utilisateur
          </button>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="w-4 h-4 absolute left-3 top-3 text-on-surface-variant" />
          <input
            type="text"
            placeholder="Rechercher par nom, email, identifiant..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2 text-sm bg-surface-container-low border border-outline rounded-xl text-on-surface focus:outline-none focus:border-primary"
          />
        </div>

        <select
          value={roleFilter}
          onChange={(e) => setRoleFilter(e.target.value)}
          className="sm:w-64 px-3 py-2 text-sm bg-surface-container-low border border-outline rounded-xl text-on-surface focus:outline-none focus:border-primary"
        >
          <option value="ALL">Tous les rôles</option>
          <option value="ADMIN">Administrateur Système</option>
          <option value="SUPER_ADMIN">Super Administrateur</option>
          <option value="DAF">DAF & Trésorerie</option>
          <option value="CHEF_COMPTABLE">Chef Comptable</option>
          <option value="DIRECTEUR_TRANSPORT">Directeur Transport</option>
          <option value="CHEF_PARC">Chef de Parc</option>
          <option value="TRANSITAIRE">Transitaire Agréé</option>
          <option value="CHEF_PERSONNEL">Chef du Personnel</option>
          <option value="OPERATEUR">Opérateur de Saisie</option>
          <option value="CHAUFFEUR">Chauffeur Routier</option>
          <option value="CLIENT_B2B">Client Partenaire B2B</option>
        </select>
      </div>

      {/* Users Table */}
      <div className="bg-surface border border-outline rounded-2xl overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-on-surface">
            <thead className="bg-surface-container-low text-xs font-bold text-on-surface-variant uppercase tracking-wider border-b border-outline">
              <tr>
                <th className="px-5 py-3">Utilisateur</th>
                <th className="px-5 py-3">Identifiant</th>
                <th className="px-5 py-3">Rôle & Habilitation</th>
                <th className="px-5 py-3">Dernière Connexion</th>
                <th className="px-5 py-3 text-center">Statut Compte</th>
                <th className="px-5 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-outline/30">
              {loading ? (
                <tr>
                  <td colSpan={6} className="p-12 text-center text-on-surface-variant">
                    Chargement des comptes utilisateurs...
                  </td>
                </tr>
              ) : filteredUsers.length === 0 ? (
                <tr>
                  <td colSpan={6} className="p-12 text-center">
                    <Users className="w-12 h-12 text-on-surface-variant/40 mx-auto mb-3" />
                    <h3 className="font-semibold text-on-surface text-base">Aucun utilisateur trouvé</h3>
                    <p className="text-xs text-on-surface-variant mt-1 max-w-md mx-auto">
                      Créez des accès pour les membres de vos équipes opérationnelles pour démarrer la collaboration.
                    </p>
                  </td>
                </tr>
              ) : (
                filteredUsers.map((u, idx) => (
                  <tr key={u.id || idx} className="hover:bg-surface-container/50 transition-colors">
                    <td className="px-5 py-3.5">
                      <div className="font-bold text-on-surface">{u.full_name || u.username || 'Collaborateur'}</div>
                      <div className="text-xs text-on-surface-variant flex items-center gap-1">
                        <Mail className="w-3 h-3" /> {u.email}
                      </div>
                    </td>
                    <td className="px-5 py-3.5 font-mono text-xs text-primary font-semibold">
                      {u.username || u.email?.split('@')[0]}
                    </td>
                    <td className="px-5 py-3.5 text-xs">
                      <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-surface-container border border-outline/50 font-semibold text-on-surface">
                        <Shield className="w-3 h-3 text-primary" />
                        {u.role || 'LOGISTICIEN'}
                      </span>
                    </td>
                    <td className="px-5 py-3.5 text-xs text-on-surface-variant">
                      {u.last_login ? new Date(u.last_login).toLocaleString('fr-FR').slice(0, 16) : 'Jamais connecté'}
                    </td>
                    <td className="px-5 py-3.5 text-center">
                      <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold ${
                        u.is_active !== false
                          ? 'bg-emerald-500/10 text-emerald-600'
                          : 'bg-rose-500/10 text-rose-600'
                      }`}>
                        {u.is_active !== false ? <UserCheck className="w-3 h-3" /> : <UserX className="w-3 h-3" />}
                        {u.is_active !== false ? 'Actif' : 'Désactivé'}
                      </span>
                    </td>
                    <td className="px-5 py-3.5 text-right">
                      <div className="flex items-center justify-end gap-1.5">
                        <button
                          onClick={() => handleToggleStatus(u)}
                          className="px-2 py-1 text-[11px] font-semibold border border-outline rounded-lg hover:bg-surface-container"
                          title={u.is_active !== false ? 'Désactiver le compte' : 'Activer le compte'}
                        >
                          {u.is_active !== false ? 'Verrouiller' : 'Activer'}
                        </button>
                        <button
                          onClick={() => handleResetPassword(u)}
                          className="px-2 py-1 text-[11px] font-semibold border border-outline rounded-lg hover:bg-surface-container text-primary"
                          title="Réinitialiser le mot de passe"
                        >
                          <KeyRound className="w-3 h-3 inline" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal Creation */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-surface border border-outline rounded-2xl w-full max-w-md p-6 space-y-4 text-on-surface shadow-2xl">
            <div className="flex justify-between items-center pb-2 border-b border-outline">
              <h2 className="text-lg font-bold flex items-center gap-2">
                <Users className="w-5 h-5 text-primary" /> Créer un Compte Collaborateur
              </h2>
              <button onClick={() => setIsModalOpen(false)} className="text-on-surface-variant hover:text-on-surface">✕</button>
            </div>

            <form onSubmit={handleCreateUser} className="space-y-3">
              <div>
                <label className="block text-xs font-semibold mb-1">Nom et Prénom *</label>
                <input
                  type="text"
                  required
                  placeholder="Ex: Jean-Paul MBIIDA"
                  value={newUser.full_name}
                  onChange={e => setNewUser({ ...newUser, full_name: e.target.value })}
                  className="w-full px-3 py-2 text-sm bg-surface-container-low border border-outline rounded-xl"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold mb-1">Identifiant de Connexion *</label>
                <input
                  type="text"
                  required
                  placeholder="Ex: jmbiida"
                  value={newUser.username}
                  onChange={e => setNewUser({ ...newUser, username: e.target.value })}
                  className="w-full px-3 py-2 text-sm bg-surface-container-low border border-outline rounded-xl font-mono"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold mb-1">Email Professionnel *</label>
                <input
                  type="email"
                  required
                  placeholder="Ex: jmbiida@evo-logistics.cm"
                  value={newUser.email}
                  onChange={e => setNewUser({ ...newUser, email: e.target.value })}
                  className="w-full px-3 py-2 text-sm bg-surface-container-low border border-outline rounded-xl"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold mb-1">Mot de Passe Initial *</label>
                <input
                  type="password"
                  required
                  placeholder="••••••••••••"
                  value={newUser.password}
                  onChange={e => setNewUser({ ...newUser, password: e.target.value })}
                  className="w-full px-3 py-2 text-sm bg-surface-container-low border border-outline rounded-xl"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold mb-1">Rôle Affecté *</label>
                <select
                  value={newUser.role}
                  onChange={e => setNewUser({ ...newUser, role: e.target.value })}
                  className="w-full px-3 py-2 text-sm bg-surface-container-low border border-outline rounded-xl"
                >
                  <option value="ADMIN">Administrateur Système</option>
                  <option value="DIRECTEUR_GENERAL">Direction Générale</option>
                  <option value="RESPONSABLE_TRANSIT">Responsable Transit</option>
                  <option value="DECLARANT_DOUANE">Déclarant en Douane</option>
                  <option value="GESTIONNAIRE_FLOTTE">Gestionnaire de Flotte GMAO</option>
                  <option value="MAGASINIER">Chef Magasinier WMS</option>
                  <option value="COMPTABLE">Comptable / DAF</option>
                  <option value="CHEF_PERSONNEL">Chef du Personnel (N+1)</option>
                  <option value="OPERATEUR_SAISIE">Opérateur de Saisie</option>
                </select>
              </div>

              <div className="flex justify-end gap-2 pt-3 border-t border-outline">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 text-xs font-semibold border border-outline rounded-xl"
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-4 py-2 text-xs font-semibold bg-primary text-on-primary rounded-xl"
                >
                  {submitting ? 'Création...' : 'Créer le Compte'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
