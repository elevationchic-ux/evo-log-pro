/**
 * API Client for Cameroon/CEMAC Modules
 * Connects frontend to backend endpoints
 */

import api from './api'

// Types for Cameroon/CEMAC modules
export interface BSC {
  id: number
  numero_bsc: string
  numero_connaisse: string
  navire: string
  port_chargement: string
  port_dechargement: string
  date_emission: string
  agent: string
  montant_frais: number
  statut: string
}

export interface CSC {
  id: number
  bsc_id: number
  date_inspection: string
  type_marchandise: string
  statut: string
}

export interface DUM {
  id: number
  navire: string
  numero_connaisse: string
  regime: string
  valeur_cif: number
  statut: string
}

export interface APE {
  id: number
  navire: string
  date_arrivee: string
  nombre_conteneurs: number
  statut: string
}

export interface PaiementLocal {
  id: number
  type_paiement: string
  reference: string
  montant: number
  devise: string
  beneficiaire: string
  banque?: string
  compte?: string
  date_paiement: string
  statut: string
}

export interface DeclarationFiscale {
  id: number
  company_id: number
  type_impot: string
  periode_debut: string
  periode_fin: string
  chiffre_affaires: number
  benefice: number
  montant_du: number
  montant_paye: number
  reste_a_payer: number
  statut: string
  reference_declaration: string
}

export interface RetenueSource {
  id: number
  company_id: number
  type_retenue: string
  montant_brut: number
  taux_retenue: number
  montant_retenue: number
  montant_net: number
  beneficiaire: string
  numero_contribuable: string
  date_operation: string
  statut: string
}

// Integration Cameroun API
// NB : le backend FastAPI attend ces scalaires en paramètres de REQUÊTE (query),
// pas dans le corps JSON  d'où l'usage de { params } au lieu du second argument de post().
export const integrationCamerounApi = {
  // BSC
  creerBSC: async (data: {
    numero_connaisse: string
    navire: string
    port_chargement: string
    port_dechargement: string
    agent: string
    importateur: string
    poids_total?: number
    valeur_fob?: number
  }) => {
    const response = await api.post('/api/v1/integration-cameroun/bsc', null, { params: data })
    return response.data
  },

  listerBSC: async (params?: { skip?: number; limit?: number }) => {
    const response = await api.get('/api/v1/integration-cameroun/bsc', { params })
    return response.data
  },

  getBSC: async (bscId: number) => {
    const response = await api.get(`/api/v1/integration-cameroun/bsc/${bscId}`)
    return response.data
  },

  // CSC
  demanderCSC: async (data: {
    numero_connaisse: string
    navire: string
    port_origine: string
    port_destination: string
    type_marchandise?: string
    poids_brut_tonnes?: number
    nombre_colis?: number
    valeur_fob?: number
  }) => {
    const response = await api.post('/api/v1/integration-cameroun/csc', null, { params: data })
    return response.data
  },

  listerCSC: async (params?: { skip?: number; limit?: number }) => {
    const response = await api.get('/api/v1/integration-cameroun/csc', { params })
    return response.data
  },

  // DUM
  creerDUM: async (data: {
    type_operation: string
    regime_douanier: string
    bureau_douane: string
    declarant: string
    importateur: string
    marchandise: string
    valeur_fob?: number
    taux_change?: number
    poids_brut?: number
    nombre_colis?: number
  }) => {
    const response = await api.post('/api/v1/integration-cameroun/dum', null, { params: data })
    return response.data
  },

  listerDUM: async (params?: { skip?: number; limit?: number }) => {
    const response = await api.get('/api/v1/integration-cameroun/dum', { params })
    return response.data
  },

  // APE
  creerAPE: async (data: {
    importateur: string
    montant_xaf: number
    devise: string
    banque: string
    beneficiaire_etranger?: string
    pays_beneficiaire?: string
    objet_transfert?: string
  }) => {
    const response = await api.post('/api/v1/integration-cameroun/ape', null, { params: data })
    return response.data
  },

  listerAPE: async (params?: { skip?: number; limit?: number }) => {
    const response = await api.get('/api/v1/integration-cameroun/ape', { params })
    return response.data
  },

  // Tarifs Douane
  getTarifsDouane: async () => {
    const response = await api.get('/api/v1/integration-cameroun/tarifs-douane')
    return response.data
  },

  // Calculer Droits
  calculerDroits: async (data: {
    valeur_cif: number
    taux_douane?: number
    tva?: number
  }) => {
    const response = await api.post('/api/v1/integration-cameroun/calculer-droits', null, { params: data })
    return response.data
  }
}

// Paiement Local API
export const paiementLocalApi = {
  // Initier paiement
  initierPaiement: async (methode: string, donnees: any) => {
    const response = await api.post('/api/v1/paiement-local/initier', {
      methode,
      donnees
    })
    return response.data
  },

  // Orange Money
  initierOrangeMoney: async (data: {
    numero: string
    montant: number
    reference: string
    description: string
  }) => {
    const response = await api.post('/api/v1/paiement-local/orange-money', data)
    return response.data
  },

  verifierOrangeMoney: async (reference: string) => {
    const response = await api.get(`/api/v1/paiement-local/orange-money/${reference}/verifier`)
    return response.data
  },

  // MTN
  initierMTN: async (data: {
    numero: string
    montant: number
    reference: string
    description: string
  }) => {
    const response = await api.post('/api/v1/paiement-local/mtn', data)
    return response.data
  },

  verifierMTN: async (reference: string) => {
    const response = await api.get(`/api/v1/paiement-local/mtn/${reference}/verifier`)
    return response.data
  },

  // Virement
  initierVirement: async (data: {
    banque: string
    compte: string
    montant: number
    beneficiaire: string
    reference: string
    motif: string
  }) => {
    const response = await api.post('/api/v1/paiement-local/virement', data)
    return response.data
  },

  // Méthodes disponibles
  getMethodesDisponibles: async () => {
    const response = await api.get('/api/v1/paiement-local/methodes')
    return response.data
  }
}

// Fiscalité Cameroun API
// NB : scalaires attendus en paramètres de requête par FastAPI (voir commentaire plus haut).
export const fiscaliteCamerounApi = {
  // Déclarations
  creerDeclaration: async (data: {
    company_id: number
    type_impot: string
    periode_debut: string
    periode_fin: string
    chiffre_affaires: number
    benefice: number
  }) => {
    const response = await api.post('/api/v1/fiscalite-cameroun/declarations', null, { params: data })
    return response.data
  },

  soumettreDeclaration: async (declarationId: number) => {
    const response = await api.post(`/api/v1/fiscalite-cameroun/declarations/${declarationId}/soumettre`)
    return response.data
  },

  validerDeclaration: async (declarationId: number, agentFiscal: string) => {
    const response = await api.post(
      `/api/v1/fiscalite-cameroun/declarations/${declarationId}/valider`,
      null,
      { params: { agent_fiscal: agentFiscal } }
    )
    return response.data
  },

  payerDeclaration: async (declarationId: number, montant: number) => {
    const response = await api.post(
      `/api/v1/fiscalite-cameroun/declarations/${declarationId}/payer`,
      null,
      { params: { montant } }
    )
    return response.data
  },

  // Retenues Source
  creerRetenueSource: async (data: {
    company_id: number
    type_retenue: string
    montant_brut: number
    beneficiaire: string
    numero_contribuable: string
  }) => {
    const response = await api.post('/api/v1/fiscalite-cameroun/retenues-source', null, { params: data })
    return response.data
  },

  verserRetenue: async (retenueId: number) => {
    const response = await api.post(`/api/v1/fiscalite-cameroun/retenues-source/${retenueId}/verser`)
    return response.data
  },

  // OHADA
  calculerTVA: async (montantHt: number, tauxTva: number = 19.25) => {
    const response = await api.post(
      '/api/v1/fiscalite-cameroun/ohada/tva',
      null,
      { params: { montant_ht: montantHt, taux_tva: tauxTva } }
    )
    return response.data
  },

  calculerCentimes: async (montant: number, taux: number = 10) => {
    const response = await api.post(
      '/api/v1/fiscalite-cameroun/ohada/centimes',
      null,
      { params: { montant, taux } }
    )
    return response.data
  },

  calculerISMinimum: async (chiffreAffaires: number) => {
    const response = await api.post(
      '/api/v1/fiscalite-cameroun/ohada/is-minimum',
      null,
      { params: { chiffre_affaires: chiffreAffaires } }
    )
    return response.data
  },

  // Rapports
  genererBilan: async (companyId: number, exercice: number) => {
    const response = await api.get(`/api/v1/fiscalite-cameroun/ohada/bilan/${companyId}/${exercice}`)
    return response.data
  },

  genererCompteResultat: async (companyId: number, exercice: number) => {
    const response = await api.get(`/api/v1/fiscalite-cameroun/ohada/compte-resultat/${companyId}/${exercice}`)
    return response.data
  }
}
