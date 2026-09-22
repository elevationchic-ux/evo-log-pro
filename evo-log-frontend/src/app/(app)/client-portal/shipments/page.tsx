'use client';

import React, { useEffect, useState } from 'react';
import {
  Truck,
  Calendar,
  MapPin,
  Package,
  CheckCircle2,
  AlertTriangle,
  Clock,
  RefreshCw,
  Search,
  Menu,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import { transportAPI } from '@/lib/api-client';

export default function ClientShipmentsPage() {
  const [missions, setMissions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedMission, setSelectedMission] = useState<any>(null);
  const [filters, setFilters] = useState({
    statut: '',
    dateDebut: '',
    dateFin: '',
    search: ''
  });
  const [sortBy, setSortBy] = useState<{ field: string; direction: 'asc' | 'desc' }>({
    field: 'dateCreation',
    direction: 'desc'
  });
  const [expandedMissionId, setExpandedMissionId] = useState<string | null>(null);

  useEffect(() => {
    loadMissions();
  }, []);

  const loadMissions = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await transportAPI.getMissions({
        limit: 100,
        ...filters,
        sortBy: `${sortBy.field}:${sortBy.direction}`
      });
      setMissions(res.data?.items || res.data || []);
    } catch (err) {
      console.error('Failed to load missions:', err);
      setError('Impossible de charger les missions. Veuillez réessayer.');
    } finally {
      setLoading(false);
    }
  };

  const handleStatusChange = (missionId: number, newStatus: string) => {
    // In a real app, this would open a modal or update via API
    console.log(`Changing mission ${missionId} status to ${newStatus}`);
    // For now, we'll just simulate
    setMissions(prev =>
      prev.map(m =>
        m.id === missionId ? { ...m, statut: newStatus } : m
      )
    );
    if (selectedMission?.id === missionId) {
      setSelectedMission((prev: any) => prev ? { ...prev, statut: newStatus } : null);
    }
  };

  const handleToggleExpand = (missionId: string) => {
    setExpandedMissionId(expandedMissionId === missionId ? null : missionId);
  };

  const filteredMissions = missions.filter(mission => {
    if (filters.statut && mission.statut !== filters.statut) return false;
    if (filters.search) {
      const searchTerm = filters.search.toLowerCase();
      return (
        mission.reference?.toLowerCase().includes(searchTerm) ||
        mission.lieu_depart?.toLowerCase().includes(searchTerm) ||
        mission.lieu_arrivee?.toLowerCase().includes(searchTerm) ||
        mission.nature_fret?.toLowerCase().includes(searchTerm)
      );
    }
    return true;
  });

  const sortedMissions = [...filteredMissions].sort((a, b) => {
    const fieldA = a[sortBy.field];
    const fieldB = b[sortBy.field];

    if (fieldA === undefined || fieldA === null) return 1;
    if (fieldB === undefined || fieldB === null) return -1;

    if (sortBy.direction === 'asc') {
      return fieldA > fieldB ? 1 : -1;
    } else {
      return fieldA < fieldB ? 1 : -1;
    }
  });

  return (
    <div className="min-h-[80vh] py-12">
      {/* Header */}
      <div className="mb-8">
        <div className="flex justify-between items-start sm:items-center sm:justify-between flex-wrap gap-4">
          <div>
            <h1 className="text-3xl font-bold text-slate-900 mb-2">
              Mes Expéditions
            </h1>
            <p className="text-slate-600">
              Suivez l'état de toutes vos expéditions en temps réel
            </p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => setSelectedMission(null)}
              className="btn btn-primary btn-sm flex items-center gap-2"
            >
              <Package className="w-4 h-4" /> Nouvelle Expédition
            </button>
            <button
              onClick={loadMissions}
              className="btn btn-outline btn-sm flex items-center gap-2"
            >
              <RefreshCw className="w-4 h-4" /> Actualiser
            </button>
          </div>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-6 p-4 bg-red-50 border-l-4 border-red-500 rounded">
          <AlertTriangle className="w-4 h-4 text-red-600 mr-2" />
          <span>{error}</span>
        </div>
      )}

      {/* Filters */}
      <div className="mb-6">
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
          <h3 className="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
            <Search className="w-5 h-5" /> Filtres
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Statut
              </label>
              <select
                value={filters.statut}
                onChange={(e) => setFilters(prev => ({ ...prev, statut: e.target.value }))}
                className="select select-bordered w-full"
              >
                <option value="">Tous les statuts</option>
                <option value="BROUILLON">Brouillon</option>
                <option value="EN_ATTENTE_AFFECTATION">Programmé</option>
                <option value="EN_CHARGEMENT">En Chargement</option>
                <option value="EN_ROUTE">En Route</option>
                <option value="LIVREE">Livré</option>
                <option value="ANNULEE">Annulé</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Date de Début
              </label>
              <input
                type="date"
                value={filters.dateDebut}
                onChange={(e) => setFilters(prev => ({ ...prev, dateDebut: e.target.value }))}
                className="input input-bordered w-full"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Date de Fin
              </label>
              <input
                type="date"
                value={filters.dateFin}
                onChange={(e) => setFilters(prev => ({ ...prev, dateFin: e.target.value }))}
                className="input input-bordered w-full"
              />
            </div>
            <div className="flex items-end">
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Recherche
              </label>
              <input
                type="text"
                placeholder="Référence, trajet, marchandise..."
                value={filters.search}
                onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value }))}
                className="input input-bordered w-full"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Statistics */}
      <div className="mb-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 text-center">
            <div className="flex items-center justify-center mb-3">
              <Truck className="w-8 h-8 text-primary" />
            </div>
            <p className="text-sm font-medium text-slate-500">Total Expéditions</p>
            <p className="text-2xl font-bold text-slate-900">{missions.length}</p>
          </div>
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 text-center">
            <div className="flex items-center justify-center mb-3">
              <CheckCircle2 className="w-8 h-8 text-success" />
            </div>
            <p className="text-sm font-medium text-slate-500">Livrées</p>
            <p className="text-2xl font-bold text-slate-900">
              {missions.filter(m => m.statut === 'LIVREE').length}
            </p>
          </div>
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 text-center">
            <div className="flex items-center justify-center mb-3">
              <MapPin className="w-8 h-8 text-warning" />
            </div>
            <p className="text-sm font-medium text-slate-500">En Cours</p>
            <p className="text-2xl font-bold text-slate-900">
              {missions.filter(m => ['EN_ROUTE', 'EN_CHARGEMENT'].includes(m.statut)).length}
            </p>
          </div>
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 text-center">
            <div className="flex items-center justify-center mb-3">
              <Calendar className="w-8 h-8 text-info" />
            </div>
            <p className="text-sm font-medium text-slate-500">À Venir</p>
            <p className="text-2xl font-bold text-slate-900">
              {missions.filter(m => m.statut === 'EN_ATTENTE_AFFECTATION').length}
            </p>
          </div>
        </div>
      </div>

      {/* Missions List */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        <div className="p-6 border-b border-slate-100 flex justify-between items-center">
          <h3 className="text-lg font-bold text-slate-800">
            Liste des Expéditions ({filteredMissions.length} résultat{(filteredMissions.length !== 1) ? 's' : ''})
          </h3>
          <div className="flex items-center gap-2 text-sm text-slate-500">
            <span>Trier par :</span>
            <select
              value={sortBy.field}
              onChange={(e) => setSortBy(prev => ({ ...prev, field: e.target.value }))}
              className="select select-sm select-bordered"
            >
              <option value="dateCreation">Date (récent)</option>
              <option value="dateCreation:asc">Date (ancien)</option>
              <option value="reference">Référence</option>
              <option value="statut">Statut</option>
              <option value="lieu_depart">Départ</option>
            </select>
          </div>
        </div>

        {loading && !missions.length && (
          <div className="p-12 text-center">
            <RefreshCw className="w-12 h-12 text-primary animate-spin mx-auto mb-4" />
            <p className="text-slate-600">Chargement des expéditions...</p>
          </div>
        )}

        {!loading && missions.length === 0 && !error && (
          <div className="p-12 text-center">
            <Package className="w-12 h-12 text-slate-400 mx-auto mb-4" />
            <p className="text-slate-500">Aucune expédition trouvée</p>
            <p className="text-slate-400 text-sm mt-2">
              Aucune expédition ne correspond aux filtres appliqués
            </p>
          </div>
        )}

        {!loading && missions.length > 0 && (
          <div className="divide-y divide-slate-100">
            {sortedMissions.map((mission) => (
              <div key={mission.id} className="cursor-pointer hover:bg-slate-50 transition-colors">
                {/* Mission Header */}
                <div className="flex justify-between items-start px-6 py-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-3">
                      <div className="w-3 h-3 rounded-full">
                        {mission.statut === 'LIVREE' && (
                          <CheckCircle2 className="w-4 h-4 text-success" />
                        )}
                        {mission.statut === 'EN_ROUTE' && (
                          <div className="w-3 h-3 border-2 border-primary" />
                        )}
                        {mission.statut === 'EN_CHARGEMENT' && (
                          <div className="w-3 h-3 border-2 border-warning" />
                        )}
                        {mission.statut === 'EN_ATTENTE_AFFECTATION' && (
                          <div className="w-3 h-3 border-2 border-info" />
                        )}
                        {mission.statut === 'BROUILLON' && (
                          <div className="w-3 h-3 border-2 border-slate-400" />
                        )}
                        {mission.statut === 'ANNULEE' && (
                          <div className="w-3 h-3 border-2 border-destructive" />
                        )}
                      </div>
                      <div>
                        <p className="font-medium text-slate-800">{mission.reference}</p>
                        <p className="text-sm text-slate-500 truncate">
                          {mission.lieu_depart} → {mission.lieu_arrivee}
                        </p>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 text-sm">
                    <span className={
                      mission.statut === 'LIVREE' ? 'badge badge-success' :
                      mission.statut === 'EN_ROUTE' ? 'badge badge-warning' :
                      mission.statut === 'EN_CHARGEMENT' ? 'badge badge-warning' :
                      mission.statut === 'EN_ATTENTE_AFFECTATION' ? 'badge badge-info' :
                      mission.statut === 'BROUILLON' ? 'badge badge-secondary' :
                      'badge badge-destructive'
                    }>
                      {mission.statut}
                    </span>
                    <button
                      onClick={() => handleToggleExpand(mission.id.toString())}
                      className="btn btn-ghost btn-sm p-1"
                      aria-label="Développer/Réduire les détails"
                    >
                      {expandedMissionId === mission.id.toString() ? (
                        <ChevronUp className="w-4 h-4" />
                      ) : (
                        <ChevronDown className="w-4 h-4" />
                      )}
                    </button>
                  </div>
                </div>

                {/* Mission Details (expandable) */}
                {expandedMissionId === mission.id.toString() && (
                  <div className="px-6 py-4 bg-slate-50 border-t border-slate-100">
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      <div className="space-y-2">
                        <p className="text-sm font-medium text-slate-700">Date de Départ Prévue</p>
                        <p className="text-slate-500">
                          {mission.date_depart_prevue ? new Date(mission.date_depart_prevue).toLocaleDateString('fr-FR') : 'Non définie'}
                        </p>
                      </div>
                      <div className="space-y-2">
                        <p className="text-sm font-medium text-slate-700">Date d'Arrivée Prévue</p>
                        <p className="text-slate-500">
                          {mission.date_arrivee_prevue ? new Date(mission.date_arrivee_prevue).toLocaleDateString('fr-FR') : 'Non définie'}
                        </p>
                      </div>
                      <div className="space-y-2">
                        <p className="text-sm font-medium text-slate-700">Chauffeur Assigné</p>
                        <p className="text-slate-500">
                          {mission.chauffeur_nom || 'Non assigné'}
                        </p>
                      </div>
                      <div className="space-y-2">
                        <p className="text-sm font-medium text-slate-700">Camion Assigné</p>
                        <p className="text-slate-500">
                          {mission.camion_immatriculation || 'Non assigné'}
                        </p>
                      </div>
                      <div className="space-y-2">
                        <p className="text-sm font-medium text-slate-700">Type de Marchandise</p>
                        <p className="text-slate-500 capitalize">
                          {mission.nature_fret || 'Non spécifiée'}
                        </p>
                      </div>
                      <div className="space-y-2">
                        <p className="text-sm font-medium text-slate-700">Poids</p>
                        <p className="text-slate-500">
                          {mission.poids_total ? `${mission.poids_total} kg` : 'Non spécifié'}
                        </p>
                      </div>
                      <div className="space-y-2">
                        <p className="text-sm font-medium text-slate-700">Volume</p>
                        <p className="text-slate-500">
                          {mission.volume_total ? `${mission.volume_total} m³` : 'Non spécifié'}
                        </p>
                      </div>
                    </div>

                    {/* Action Buttons */}
                    <div className="mt-4 pt-3 border-t border-slate-200 flex flex-col sm:flex-row gap-3">
                      <button
                        onClick={() => handleStatusChange(mission.id, 'EN_ROUTE')}
                        disabled={mission.statut !== 'EN_ATTENTE_AFFECTATION'}
                        className="btn btn-sm btn-outline btn-primary flex-1"
                      >
                        Démarrer la Mission
                      </button>
                      <button
                        onClick={() => handleStatusChange(mission.id, 'LIVREE')}
                        disabled={!['EN_ROUTE', 'EN_CHARGEMENT'].includes(mission.statut)}
                        className="btn btn-sm btn-outline btn-success flex-1"
                      >
                        Marquer comme Livré
                      </button>
                      <button
                        onClick={() => {
                          // In a real app, this would open a modal for BL generation
                          alert(`Génération du Bon de Livraison pour la mission ${mission.reference}`);
                        }}
                        disabled={mission.statut !== 'LIVREE'}
                        className="btn btn-sm btn-outline btn-info flex-1"
                      >
                        Générer BL
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Selected Mission Detail View */}
      {selectedMission && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center">
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-4xl mx-4 p-6 max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-start mb-6">
              <div>
                <h2 className="text-2xl font-bold text-slate-900">
                  Mission {selectedMission.reference}
                </h2>
                <p className="text-slate-600">
                  Détails complets de l'expédition
                </p>
              </div>
              <button
                onClick={() => setSelectedMission(null)}
                className="btn btn-ghost btn-sm"
                aria-label="Fermer"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 011.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 4.293a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
              </button>
            </div>

            <div className="space-y-6">
              {/* Mission Info */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-slate-800">Informations Générales</h3>
                  <div className="space-y-2">
                    <p className="text-sm font-medium text-slate-700">Référence</p>
                    <p className="font-mono text-slate-900">{selectedMission.reference}</p>
                  </div>
                  <div className="space-y-2">
                    <p className="text-sm font-medium text-slate-700">Statut</p>
                    <span className={
                      selectedMission.statut === 'LIVREE' ? 'badge badge-success' :
                      selectedMission.statut === 'EN_ROUTE' ? 'badge badge-warning' :
                      selectedMission.statut === 'EN_CHARGEMENT' ? 'badge badge-warning' :
                      selectedMission.statut === 'EN_ATTENTE_AFFECTATION' ? 'badge badge-info' :
                      selectedMission.statut === 'BROUILLON' ? 'badge badge-secondary' :
                      'badge badge-destructive'
                    }>
                      {selectedMission.statut}
                    </span>
                  </div>
                  <div className="space-y-2">
                    <p className="text-sm font-medium text-slate-700">Date de Création</p>
                    <p className="text-slate-500">
                      {selectedMission.dateCreation ? new Date(selectedMission.dateCreation).toLocaleDateString('fr-FR') : 'Non définie'}
                    </p>
                  </div>
                </div>

                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-slate-800">Itinéraire</h3>
                  <div className="space-y-2">
                    <p className="text-sm font-medium text-slate-700">Départ</p>
                    <p className="text-slate-500">{selectedMission.lieu_depart || 'Non défini'}</p>
                  </div>
                  <div className="space-y-2">
                    <p className="text-sm font-medium text-slate-700">Arrivée</p>
                    <p className="text-slate-500">{selectedMission.lieu_arrivee || 'Non défini'}</p>
                  </div>
                  <div className="space-y-2">
                    <p className="text-sm font-medium text-slate-700">Distance Estimée</p>
                    <p className="text-slate-500">
                      {selectedMission.distance_estimee ? `${selectedMission.distance_estimee} km` : 'Non définie'}
                    </p>
                  </div>
                </div>

                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-slate-800">Détails du Fret</h3>
                  <div className="space-y-2">
                    <p className="text-sm font-medium text-slate-700">Nature du Fret</p>
                    <p className="text-slate-500 capitalize">{selectedMission.nature_fret || 'Non spécifié'}</p>
                  </div>
                  <div className="space-y-2">
                    <p className="text-sm font-medium text-slate-700">Poids Total</p>
                    <p className="text-slate-500">
                      {selectedMission.poids_total ? `${selectedMission.poids_total} kg` : 'Non spécifié'}
                    </p>
                  </div>
                  <div className="space-y-2">
                    <p className="text-sm font-medium text-slate-700">Volume Total</p>
                    <p className="text-slate-500">
                      {selectedMission.volume_total ? `${selectedMission.volume_total} m³` : 'Non spécifié'}
                    </p>
                  </div>
                  <div className="space-y-2">
                    <p className="text-sm font-medium text-slate-700">Nombre de Colis</p>
                    <p className="text-slate-500">{selectedMission.nombre_colis || 'Non spécifié'}</p>
                  </div>
                </div>
              </div>

              {/* Timeline */}
              <div className="lg:col-span-3">
                <h3 className="text-lg font-semibold text-slate-800">Historique et Suivi</h3>
                <div className="space-y-4">
                  {/* Timeline items would go here */}
                  <div className="border-l-2 border-slate-200 pl-4">
                    {/* Example timeline entry */}
                    <div className="mb-4 pb-4 border-b border-slate-100 last:mb-0 last:pb-0 last:border-0">
                      <div className="flex items-start gap-3">
                        <div className="w-3 h-3 bg-success rounded-full flex items-center justify-center">
                          <CheckCircle2 className="w-4 h-4" />
                        </div>
                        <div>
                          <p className="font-medium text-slate-800">Mission créée</p>
                          <p className="text-sm text-slate-500">
                            {selectedMission.dateCreation ? new Date(selectedMission.dateCreation).toLocaleString('fr-FR') : ''}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}