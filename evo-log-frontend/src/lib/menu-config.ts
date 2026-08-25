/**
 * Menu Configuration for EVO-LOG Frontend
 * Add these entries to your existing menu configuration
 */

export const MENU_ITEMS = [
  // ... existing menu items ...
  
  // Cameroon/CEMAC Modules
  {
    id: 'integration-cameroun',
    name: 'Intégration Cameroun',
    path: '/integration-cameroun',
    icon: '🇨🇲',
    description: 'BSC, CSC, SYGED, APE',
    color: '#FF6B6B',
    category: 'Cameroon',
    roles: ['DISPATCHER', 'DOUANE', 'ADMIN']
  },
  {
    id: 'paiement-local',
    name: 'Paiements Locaux',
    path: '/paiement-local',
    icon: '💳',
    description: 'Orange Money, MTN, Banques',
    color: '#4ECDC4',
    category: 'Cameroon',
    roles: ['FINANCIER', 'ADMIN']
  },
  {
    id: 'fiscalite-cameroun',
    name: 'Fiscalité Cameroun',
    path: '/fiscalite-cameroun',
    icon: '📊',
    description: 'IRPP, IS, TCF, TDR, OHADA',
    color: '#96CEB4',
    category: 'Cameroon',
    roles: ['FINANCIER', 'ADMIN']
  }
]

export const MENU_CATEGORIES = [
  // ... existing categories ...
  {
    id: 'cameroon',
    name: 'Cameroun/CEMAC',
    color: '#FF6B6B',
    icon: '🇨🇲'
  }
]
