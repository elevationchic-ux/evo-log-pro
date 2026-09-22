'use client';

import React, { useEffect, useState } from 'react';
import {
  MessageCircle,
  RefreshCw,
  CheckCircle2,
  AlertTriangle,
  ChevronDown,
  ChevronUp,
  Calendar,
  TrendingUp,
  Users,
  Search
} from 'lucide-react';
import { supportAPI } from '@/lib/api-client';

export default function ClientTicketPage() {
  const [incidents, setIncidents] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState({
    statut: '',
    priorite: '',
    dateDebut: '',
    dateFin: '',
    search: ''
  });
  const [sortBy, setSortBy] = useState<{ field: string; direction: 'asc' | 'desc' }>({
    field: 'dateCreation',
    direction: 'desc'
  });
  const [selectedIncident, setSelectedIncident] = useState<any>(null);

  useEffect(() => {
    loadIncidents();
  }, []);

  const loadIncidents = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await supportAPI.getIncidents({
        limit: 100,
        ...filters
      });
      setIncidents(res.data?.items || res.data || []);
    } catch (err) {
      console.error('Failed to load incidents:', err);
      setError('Impossible de charger les litiges. Veuillez réessayer.');
    } finally {
      setLoading(false);
    }
  };

  const filteredIncidents = incidents.filter(incident => {
    if (filters.statut && incident.statut !== filters.statut) return false;
    if (filters.priorite && incident.priorite !== filters.priorite) return false;
    if (filters.search) {
      const searchTerm = filters.search.toLowerCase();
      return (
        incident.id?.toString().toLowerCase().includes(searchTerm) ||
        (incident.titre || '').toLowerCase().includes(searchTerm) ||
        (incident.description || '').toLowerCase().includes(searchTerm)
      );
    }
    return true;
  });

  const sortedIncidents = [...filteredIncidents].sort((a, b) => {
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
              Mes Litiges & Suivi
            </h1>
            <p className="text-slate-600">
              Gérez vos réclamations, suivi des incidents et communication avec le support
            </p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => {
                window.location.href = '/support';
              }}
              className="btn btn-primary btn-sm flex items-center gap-2"
            >
              <MessageCircle className="w-4 h-4" /> Nouveau Litige
            </button>
            <button
              onClick={loadIncidents}
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
                <option value="OUVERT">Ouvert</option>
                <option value="EN_COURS">En Cours</option>
                <option value="RESOLU">Résolu</option>
                <option value="FERME">Fermé</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Priorité
              </label>
              <select
                value={filters.priorite}
                onChange={(e) => setFilters(prev => ({ ...prev, priorite: e.target.value }))}
                className="select select-bordered w-full"
              >
                <option value="">Toutes les priorités</option>
                <option value="BASSE">Basse</option>
                <option value="MOYENNE">Moyenne</option>
                <option value="HAUTE">Haute</option>
                <option value="URGENTE">Urgente</option>
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
                placeholder="Numéro, titre, description..."
                value={filters.search}
                onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value }))}
                className="input input-bordered w-full"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Incidents List */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        <div className="p-6 border-b border-slate-100 flex justify-between items-center">
          <h3 className="text-lg font-bold text-slate-800">
            Liste des Litiges ({filteredIncidents.length} résultat{(filteredIncidents.length !== 1) ? 's' : ''})
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
              <option value="titre">Titre</option>
              <option value="statut">Statut</option>
              <option value="priorite">Priorité</option>
            </select>
          </div>
        </div>

        {loading && !incidents.length && (
          <div className="p-12 text-center">
            <RefreshCw className="w-12 h-12 text-primary animate-spin mx-auto mb-4" />
            <p className="text-slate-600">Chargement des litiges...</p>
          </div>
        )}

        {!loading && incidents.length === 0 && !error && (
          <div className="p-12 text-center">
            <MessageCircle className="w-12 h-12 text-slate-400 mx-auto mb-4" />
            <p className="text-slate-500">Aucun litige trouvé</p>
            <p className="text-slate-400 text-sm mt-2">
              Aucun litige ne correspond aux filtres appliqués
            </p>
          </div>
        )}

        {!loading && incidents.length > 0 && (
          <div className="divide-y divide-slate-100">
            {sortedIncidents.map((incident) => (
              <div key={incident.id} className="cursor-pointer hover:bg-slate-50 transition-colors">
                {/* Incident Header */}
                <div className="flex justify-between items-start px-6 py-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-3">
                      <div className="w-3 h-3 rounded-full">
                        {incident.statut === 'RESOLU' && (
                          <CheckCircle2 className="w-4 h-4 text-success" />
                        )}
                        {incident.statut === 'EN_COURS' && (
                          <div className="w-3 h-3 border-2 border-warning" />
                        )}
                        {incident.statut === 'OUVERT' && (
                          <div className="w-3 h-3 border-2 border-info" />
                        )}
                        {incident.statut === 'FERME' && (
                          <div className="w-3 h-3 border-2 border-success" />
                        )}
                      </div>
                      <div>
                        <p className="font-medium text-slate-800">{incident.titre}</p>
                        <p className="text-sm text-slate-500 truncate">
                          {incident.description?.substring(0, 50)}...
                        </p>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 text-sm">
                    <span className={
                      incident.statut === 'RESOLU' ? 'badge badge-success' :
                      incident.statut === 'EN_COURS' ? 'badge badge-warning' :
                      incident.statut === 'OUVERT' ? 'badge badge-info' :
                      'badge badge-secondary'
                    }>
                      {incident.statut}
                    </span>
                    <p className="text-slate-500">
                      {incident.priorite === 'URGENTE' && (
                        <span className="badge badge-destructive">URGENTE</span>
                      )}
                      {incident.priorite === 'HAUTE' && (
                        <span className="badge badge-warning">HAUTE</span>
                      )}
                      {incident.priorite === 'MOYENNE' && (
                        <span className="badge badge-info">MOYENNE</span>
                      )}
                      {incident.priorite === 'BASSE' && (
                        <span className="badge badge-secondary">BASSE</span>
                      )}
                    </p>
                    <button
                      onClick={() => setSelectedIncident(incident)}
                      className="btn btn-ghost btn-sm p-1"
                      aria-label="Développer/Réduire les détails"
                    >
                      {selectedIncident?.id === incident.id ? (
                        <ChevronUp className="w-4 h-4" />
                      ) : (
                        <ChevronDown className="w-4 h-4" />
                      )}
                    </button>
                  </div>
                </div>

                {/* Incident Details (expandable) */}
                {selectedIncident?.id === incident.id && (
                  <div className="px-6 py-4 bg-slate-50 border-t border-slate-100">
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                      <div className="space-y-4">
                        <h3 className="text-lg font-semibold text-slate-800">Informations Générales</h3>
                        <div className="space-y-2">
                          <p className="text-sm font-medium text-slate-700">Numéro</p>
                          <p className="font-mono text-slate-900">#{incident.id}</p>
                        </div>
                        <div className="space-y-2">
                          <p className="text-sm font-medium text-slate-700">Titre</p>
                          <p className="text-slate-500">{incident.titre}</p>
                        </div>
                        <div className="space-y-2">
                          <p className="text-sm font-medium text-slate-700">Date de Création</p>
                          <p className="text-slate-500">
                            {incident.dateCreation ? new Date(incident.dateCreation).toLocaleDateString('fr-FR') : 'Non définie'}
                          </p>
                        </div>
                        <div className="space-y-2">
                          <p className="text-sm font-medium text-slate-700">Priorité</p>
                          <span className={
                            incident.priorite === 'URGENTE' ? 'badge badge-destructive' :
                            incident.priorite === 'HAUTE' ? 'badge badge-warning' :
                            incident.priorite === 'MOYENNE' ? 'badge badge-info' :
                            'badge badge-secondary'
                          }>
                            {incident.priorite}
                          </span>
                        </div>
                        <div className="space-y-2">
                          <p className="text-sm font-medium text-slate-700">Statut</p>
                          <span className={
                            incident.statut === 'RESOLU' ? 'badge badge-success' :
                            incident.statut === 'EN_COURS' ? 'badge badge-warning' :
                            incident.statut === 'OUVERT' ? 'badge badge-info' :
                            incident.statut === 'FERME' ? 'badge badge-success' :
                            'badge badge-secondary'
                          }>
                            {incident.statut}
                          </span>
                        </div>
                        <div className="space-y-2">
                          <p className="text-sm font-medium text-slate-700">Auteur</p>
                          <p className="text-slate-500">{incident.auteur_nom || 'Non spécifié'}</p>
                        </div>
                      </div>

                      <div className="space-y-4">
                        <h3 className="text-lg font-semibold text-slate-800">Description</h3>
                        <p className="text-slate-500">
                          {incident.description}
                        </p>
                      </div>

                      <div className="space-y-4">
                        <h3 className="text-lg font-semibold text-slate-800">Historique et Suivi</h3>
                        {incident.historique && incident.historique.length > 0 ? (
                          <div className="space-y-3">
                            {incident.historique.map((histo: any, index: number) => (
                              <div key={index} className="border-l-2 border-slate-200 pl-4 mb-4">
                                <p className="text-sm font-medium text-slate-700">
                                  {histo.auteur || 'Utilisateur'} - {new Date(histo.date).toLocaleDateString('fr-FR')}
                                </p>
                                <p className="text-slate-500">{histo.action}</p>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <div className="p-4 text-center text-slate-500">
                            Aucun historique disponible
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Action Buttons */}
                    <div className="mt-4 pt-3 border-t border-slate-200 flex flex-col sm:flex-row gap-3">
                      {incident.statut === 'OUVERT' && (
                        <>
                          <button
                            onClick={() => {
                              // In a real app, this would update status to EN_COURS
                              alert(`Marquage du litige #${incident.id} comme EN COURS`);
                            }}
                            className="btn btn-sm btn-outline btn-warning flex-1"
                          >
                            Commencer le Traitement
                          </button>
                          <button
                            onClick={() => {
                              // In a real app, this would add a comment or update
                              alert(`Ajout d'un commentaire au litige #${incident.id}`);
                            }}
                            className="btn btn-sm btn-outline btn-info flex-1"
                          >
                            Ajouter un Commentaire
                          </button>
                        </>
                      )}
                      {incident.statut === 'EN_COURS' && (
                        <>
                          <button
                            onClick={() => {
                              // In a real app, this would resolve the incident
                              alert(`Résolution du litige #${incident.id}`);
                            }}
                            className="btn btn-sm btn-outline btn-success flex-1"
                          >
                            Résoudre
                          </button>
                          <button
                            onClick={() => {
                              // In a real app, this would reopen or add comment
                              alert(`Réouverture du litige #${incident.id}`);
                            }}
                            className="btn btn-sm btn-outline btn-warning flex-1"
                          >
                            Rouvrir
                          </button>
                        </>
                      )}
                      {(incident.statut === 'RESOLU' || incident.statut === 'FERME') && (
                        <button
                          onClick={() => {
                            // In a real app, this would reopen the incident
                            alert(`Réouverture du litige #${incident.id}`);
                          }}
                          className="btn btn-sm btn-outline btn-warning flex-1"
                        >
                          Réouvrir
                        </button>
                      )}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Selected Incident Detail View */}
      {selectedIncident && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center">
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-4xl mx-4 p-6 max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-start mb-6">
              <div>
                <h2 className="text-2xl font-bold text-slate-900">
                  Litige #{selectedIncident.id}
                </h2>
                <p className="text-slate-600">
                  Détails complets du litige
                </p>
              </div>
              <button
                onClick={() => setSelectedIncident(null)}
                className="btn btn-ghost btn-sm"
                aria-label="Fermer"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 011.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 4.293a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
              </button>
            </div>

            <div className="space-y-6">
              {/* Incident Info */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-slate-800">Informations Générales</h3>
                  <div className="space-y-2">
                    <p className="text-sm font-medium text-slate-700">Numéro</p>
                    <p className="font-mono text-slate-900">#{selectedIncident.id}</p>
                  </div>
                  <div className="space-y-2">
                    <p className="text-sm font-medium text-slate-700">Titre</p>
                    <p className="text-slate-500">{selectedIncident.titre}</p>
                  </div>
                  <div className="space-y-2">
                    <p className="text-sm font-medium text-slate-700">Date de Création</p>
                    <p className="text-slate-500">
                      {selectedIncident.dateCreation ? new Date(selectedIncident.dateCreation).toLocaleDateString('fr-FR') : 'Non définie'}
                    </p>
                  </div>
                  <div className="space-y-2">
                    <p className="text-sm font-medium text-slate-700">Date de Mise à Jour</p>
                    <p className="text-slate-500">
                      {selectedIncident.dateModification ? new Date(selectedIncident.dateModification).toLocaleDateString('fr-FR') : 'Non définie'}
                    </p>
                  </div>
                  <div className="space-y-2">
                    <p className="text-sm font-medium text-slate-700">Priorité</p>
                    <span className={
                      selectedIncident.priorite === 'URGENTE' ? 'badge badge-destructive' :
                      selectedIncident.priorite === 'HAUTE' ? 'badge badge-warning' :
                      selectedIncident.priorite === 'MOYENNE' ? 'badge badge-info' :
                      'badge badge-secondary'
                    }>
                      {selectedIncident.priorite}
                    </span>
                  </div>
                  <div className="space-y-2">
                    <p className="text-sm font-medium text-slate-700">Statut</p>
                    <span className={
                      selectedIncident.statut === 'RESOLU' ? 'badge badge-success' :
                      selectedIncident.statut === 'EN_COURS' ? 'badge badge-warning' :
                      selectedIncident.statut === 'OUVERT' ? 'badge badge-info' :
                      selectedIncident.statut === 'FERME' ? 'badge badge-success' :
                      'badge badge-secondary'
                    }>
                      {selectedIncident.statut}
                    </span>
                  </div>
                  <div className="space-y-2">
                    <p className="text-sm font-medium text-slate-700">Auteur</p>
                    <p className="text-slate-500">{selectedIncident.auteur_nom || 'Non spécifié'}</p>
                  </div>
                </div>

                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-slate-800">Description Détaillée</h3>
                  <p className="text-slate-500">
                    {selectedIncident.description}
                  </p>
                </div>

                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-slate-800">Actions Requises</h3>
                  {selectedIncident.actions_requises && selectedIncident.actions_requises.length > 0 ? (
                    <ul className="list-disc list-inside space-y-2">
                      {selectedIncident.actions_requises.map((action: any, index: number) => (
                        <li key={index} className="text-slate-500">
                          {action}
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-slate-500 text-center">
                      Aucune action spécifique requise
                    </p>
                  )}
                </div>

                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-slate-800">Historique Complet</h3>
                  {selectedIncident.historique && selectedIncident.historique.length > 0 ? (
                    <div className="space-y-3">
                      {selectedIncident.historique.map((histo: any, index: number) => (
                        <div key={index} className="border-l-2 border-slate-200 pl-4 mb-4 last:mb-0">
                          <div className="flex items-start gap-3">
                            <div className="w-3 h-3 bg-slate-200 rounded-full flex items-center justify-center">
                              <Calendar className="w-4 h-4 text-slate-500" />
                            </div>
                            <div>
                              <p className="text-sm font-medium text-slate-700">
                                {histo.auteur || 'Utilisateur'} - {new Date(histo.date).toLocaleDateString('fr-FR')}
                              </p>
                              <p className="text-slate-500">{histo.action}</p>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="p-4 text-center text-slate-500">
                      Aucun historique disponible
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
          </div>
        )}
      </div>
  );
}