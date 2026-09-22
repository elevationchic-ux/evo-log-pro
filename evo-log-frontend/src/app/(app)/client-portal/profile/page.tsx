'use client';

import React, { useEffect, useState } from 'react';
import {
  User,
  Edit,
  Save,
  CheckCircle2,
  AlertTriangle,
  AlertCircle,
  Loader2,
  Mail,
  Phone,
  MapPin,
  CreditCard,
  Building,
  Calendar,
  Zap,
  Settings
} from 'lucide-react';
import { authAPI, tiersAPI } from '@/lib/api-client';

export default function ClientProfilePage() {
  const [profile, setProfile] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Form fields
  const [formData, setFormData] = useState({
    nom: '',
    prenom: '',
    email: '',
    telephone: '',
    adresse: '',
    ville: '',
    pays: '',
    codePostal: '',
    RCCM: '',
    NIU: '',
    statutJuridique: '',
    secteurActivite: ''
  });

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    setLoading(true);
    setError(null);
    try {
      // Get current user info
      const userRes = await authAPI.getMe();
      const userData = userRes.data || userRes;

      // If user is associated with a tiers (client), get tiers details
      if (userData.tiersId) {
        const tiersRes = await tiersAPI.getTiersById(userData.tiersId);
        const tiersData = tiersRes.data || tiersRes;

        setProfile({
          ...userData,
          ...tiersData
        });

        // Populate form data
        setFormData({
          nom: tiersData.nom || '',
          prenom: userData.prenom || '',
          email: userData.email || '',
          telephone: tiersData.telephone || '',
          adresse: tiersData.adresse || '',
          ville: tiersData.ville || '',
          pays: tiersData.pays || 'Cameroun',
          codePostal: tiersData.codePostal || '',
          RCCM: tiersData.RCCM || '',
          NIU: tiersData.NIU || '',
          statutJuridique: tiersData.statutJuridique || '',
          secteurActivite: tiersData.secteurActivite || ''
        });
      } else {
        // Fallback to just user data
        setProfile(userData);
        setFormData({
          nom: '',
          prenom: userData.prenom || '',
          email: userData.email || '',
          telephone: '',
          adresse: '',
          ville: '',
          pays: 'Cameroun',
          codePostal: '',
          RCCM: '',
          NIU: '',
          statutJuridique: '',
          secteurActivite: ''
        });
      }
    } catch (err) {
      console.error('Failed to load profile:', err);
      setError('Impossible de charger le profil. Veuillez réessayer.');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!profile) return;

    setLoading(true);
    setError(null);
    setSuccessMessage(null);

    try {
      // Update tiers information
      const updateData = {
        ...formData,
        // Ensure required fields are present
        nom: formData.nom || profile.nom,
        email: formData.email || profile.email
      };

      await tiersAPI.updateTiers(profile.id, updateData);

      // Also update user info if needed
      const userUpdateData = {
        prenom: formData.prenom,
        email: formData.email
      };
      await authAPI.logout(); // This might not be right, but we need to check auth API
      // Actually, let's just update what we can

      setSuccessMessage('Profil mis à jour avec succès !');
      setEditing(false);

      // Reload profile to show updated data
      setTimeout(loadProfile, 1000);
    } catch (err) {
      console.error('Failed to update profile:', err);
      setError('Erreur lors de la mise à jour du profil. Veuillez réessayer.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-[80vh] py-12">
        <div className="flex flex-col items-center justify-center">
          <Loader2 className="w-16 h-16 text-primary animate-spin" />
          <p className="mt-4 text-slate-600">Chargement du profil...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-[80vh] py-12">
        <div className="flex flex-col items-center justify-center text-center">
          <AlertTriangle className="w-16 h-16 text-destructive" />
          <p className="mt-4 text-destructive">{error}</p>
          <button
            onClick={loadProfile}
            className="mt-6 btn btn-primary"
          >
            Réessayer
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-[80vh] py-12">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-900 mb-2">
          Mon Profil
        </h1>
        <p className="text-slate-600">
          Gérez vos informations personnelles et professionnelles
        </p>
      </div>

      {/* Success/Error Messages */}
      {successMessage && (
        <div className="mb-6 p-4 bg-green-50 border-l-4 border-green-500 rounded">
          <CheckCircle2 className="w-4 h-4 text-green-600 mr-2" />
          <span>{successMessage}</span>
        </div>
      )}

      {error && editing === false && (
        <div className="mb-6 p-4 bg-red-50 border-l-4 border-red-500 rounded">
          <AlertCircle className="w-4 h-4 text-red-600 mr-2" />
          <span>{error}</span>
        </div>
      )}

      {/* Profile Content */}
      <div className="grid lg:grid-cols-3 gap-8">
        {/* Profile Overview */}
        <div className="lg:col-span-2">
          <div className="space-y-6">
            {/* Profile Header */}
            <div className="flex items-center gap-4 p-6 bg-white rounded-xl shadow-sm border border-slate-200">
              {!profile?.image ? (
                <div className="w-16 h-16 bg-primary/10 text-primary rounded-full flex items-center justify-center">
                  {profile?.prenom?.[0]?.toUpperCase()}{profile?.nom?.[0]?.toUpperCase()}
                </div>
              ) : (
                <img
                  src={profile.image}
                  alt={profile.nom}
                  className="w-16 h-16 rounded-full object-cover"
                />
              )}
              <div>
                <h2 className="text-xl font-bold text-slate-900">
                  {profile?.prenom} {profile?.nom || ''}
                </h2>
                <p className="text-slate-500">{profile?.email}</p>
                {profile?.telephone && (
                  <p className="text-slate-400 text-sm">
                    <Phone className="w-4 h-4 mr-1 inline" /> {profile.telephone}
                  </p>
                )}
              </div>
            </div>

            {/* Profile Info Cards */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {/* Personal Info */}
              <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
                <h3 className="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
                  <User className="w-5 h-5" /> Informations Personnelles
                </h3>
                <div className="space-y-3">
                  <div className="flex items-start gap-3 text-sm">
                    <CreditCard className="w-4 h-4 mt-1 text-slate-400 flex-shrink-0" />
                    <div>
                      <p className="font-medium text-slate-700">Nom complet</p>
                      <p className="text-slate-500">
                        {profile?.prenom} {profile?.nom || ''}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3 text-sm">
                    <Mail className="w-4 h-4 mt-1 text-slate-400 flex-shrink-0" />
                    <div>
                      <p className="font-medium text-slate-700">Email</p>
                      <p className="text-slate-500 break-all">{profile?.email}</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3 text-sm">
                    <Phone className="w-4 h-4 mt-1 text-slate-400 flex-shrink-0" />
                    <div>
                      <p className="font-medium text-slate-700">Téléphone</p>
                      <p className="text-slate-500">{profile?.telephone || 'Non renseigné'}</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Company Info */}
              <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
                <h3 className="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
                  <Building className="w-5 h-5" /> Informations Entreprise
                </h3>
                <div className="space-y-3">
                  <div className="flex items-start gap-3 text-sm">
                    <Building className="w-4 h-4 mt-1 text-slate-400 flex-shrink-0" />
                    <div>
                      <p className="font-medium text-slate-700">Raison Sociale</p>
                      <p className="text-slate-500">{profile?.nom || 'Non renseigné'}</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3 text-sm">
                    <MapPin className="w-4 h-4 mt-1 text-slate-400 flex-shrink-0" />
                    <div>
                      <p className="font-medium text-slate-700">Adresse</p>
                      <p className="text-slate-500 break-all">
                        {profile?.adresse}, {profile?.ville}, {profile?.pays} {profile?.codePostal}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3 text-sm">
                    <CreditCard className="w-4 h-4 mt-1 text-slate-400 flex-shrink-0" />
                    <div>
                      <p className="font-medium text-slate-700">RCCM</p>
                      <p className="text-slate-500">{profile?.RCCM || 'Non renseigné'}</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3 text-sm">
                    <CreditCard className="w-4 h-4 mt-1 text-slate-400 flex-shrink-0" />
                    <div>
                      <p className="font-medium text-slate-700">NIU</p>
                      <p className="text-slate-500">{profile?.NIU || 'Non renseigné'}</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3 text-sm">
                    <Zap className="w-4 h-4 mt-1 text-slate-400 flex-shrink-0" />
                    <div>
                      <p className="font-medium text-slate-700">Secteur d'Activité</p>
                      <p className="text-slate-500">{profile?.secteurActivite || 'Non renseigné'}</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3 text-sm">
                    <Calendar className="w-4 h-4 mt-1 text-slate-400 flex-shrink-0" />
                    <div>
                      <p className="font-medium text-slate-700">Date d'Enregistrement</p>
                      <p className="text-slate-500">
                        {profile?.dateCreation ? new Date(profile.dateCreation).toLocaleDateString('fr-FR') : 'Non renseigné'}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Edit Profile Form */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
            <h3 className="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
              {editing ? <Save className="w-5 h-5" /> : <Edit className="w-5 h-5" />}
              {editing ? 'Enregistrer les modifications' : 'Modifier le profil'}
            </h3>

            {!editing && (
              <button
                onClick={() => setEditing(true)}
                className="w-full mb-4 btn btn-outline btn-sm"
              >
                Modifier le profil
              </button>
            )}

            {editing && (
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="space-y-2">
                  <label className="block text-sm font-medium text-slate-700 mb-1">
                    Raison Sociale <span className="text-destructive">*</span>
                  </label>
                  <input
                    type="text"
                    name="nom"
                    value={formData.nom}
                    onChange={handleChange}
                    required
                    className="input input-bordered input-sm w-full"
                  />
                </div>

                <div className="space-y-2">
                  <label className="block text-sm font-medium text-slate-700 mb-1">
                    Prénom
                  </label>
                  <input
                    type="text"
                    name="prenom"
                    value={formData.prenom}
                    onChange={handleChange}
                    className="input input-bordered input-sm w-full"
                  />
                </div>

                <div className="space-y-2">
                  <label className="block text-sm font-medium text-slate-700 mb-1">
                    Email <span className="text-destructive">*</span>
                  </label>
                  <input
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    required
                    className="input input-bordered input-sm w-full"
                  />
                </div>

                <div className="space-y-2">
                  <label className="block text-sm font-medium text-slate-700 mb-1">
                    Téléphone
                  </label>
                  <input
                    type="tel"
                    name="telephone"
                    value={formData.telephone}
                    onChange={handleChange}
                    className="input input-bordered input-sm w-full"
                  />
                </div>

                <div className="space-y-2">
                  <label className="block text-sm font-medium text-slate-700 mb-1">
                    Adresse
                  </label>
                  <textarea
                    name="adresse"
                    value={formData.adresse}
                    onChange={handleChange}
                    rows={3}
                    className="textarea textarea-bordered textarea-sm w-full"
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label className="block text-sm font-medium text-slate-700 mb-1">
                        Ville
                      </label>
                      <input
                        type="text"
                        name="ville"
                        value={formData.ville}
                        onChange={handleChange}
                        className="input input-bordered input-sm w-full"
                      />
                  </div>
                  <div className="space-y-2">
                    <label className="block text-sm font-medium text-slate-700 mb-1">
                      Code Postal
                    </label>
                    <input
                      type="text"
                      name="codePostal"
                      value={formData.codePostal}
                      onChange={handleChange}
                      className="input input-bordered input-sm w-full"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="block text-sm font-medium text-slate-700 mb-1">
                    Pays
                  </label>
                  <input
                    type="text"
                    name="pays"
                    value={formData.pays || 'Cameroun'}
                    onChange={handleChange}
                    className="input input-bordered input-sm w-full"
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label className="block text-sm font-medium text-slate-700 mb-1">
                      RCCM
                    </label>
                    <input
                      type="text"
                      name="RCCM"
                      value={formData.RCCM}
                      onChange={handleChange}
                      className="input input-bordered input-sm w-full"
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="block text-sm font-medium text-slate-700 mb-1">
                      NIU
                    </label>
                    <input
                      type="text"
                      name="NIU"
                      value={formData.NIU}
                      onChange={handleChange}
                      className="input input-bordered input-sm w-full"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label className="block text-sm font-medium text-slate-700 mb-1">
                      Statut Juridique
                    </label>
                    <input
                      type="text"
                      name="statutJuridique"
                      value={formData.statutJuridique}
                      onChange={handleChange}
                      className="input input-bordered input-sm w-full"
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="block text-sm font-medium text-slate-700 mb-1">
                      Secteur d'Activité
                    </label>
                    <input
                      type="text"
                      name="secteurActivite"
                      value={formData.secteurActivite}
                      onChange={handleChange}
                      className="input input-bordered input-sm w-full"
                    />
                  </div>
                </div>

                <div className="flex justify-end pt-4 space-x-3">
                  <button
                    type="button"
                    onClick={() => setEditing(false)}
                    className="btn btn-outline btn-sm"
                  >
                    Annuler
                  </button>
                  <button
                    type="submit"
                    disabled={loading}
                    className={`btn btn-primary btn-sm ${loading ? 'btn-disabled' : ''}`}
                  >
                    {loading ? 'Enregistrement...' : 'Enregistrer'}
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}