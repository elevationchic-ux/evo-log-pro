/**
 * i18n Hook  EVO-LOG ERP
 * French / English translations covering auth, notifications, session, common UI.
 */

import { useSettings } from '@/components/layout/SettingsProvider';

const translations = {
  fr: {
    auth: {
      forgotTitle: 'Mot de passe oublié',
      forgotSubtitle: 'Entrez votre email pour réinitialiser votre mot de passe',
      forgotSuccessTitle: 'Email envoyé !',
      forgotSuccessBody: 'Si un compte existe pour cet email, vous recevrez un lien de réinitialisation.',
      forgotSpamNote: 'Pensez à vérifier votre dossier spam.',
      backToLogin: 'Retour à la connexion',
      emailInstitutionalLabel: 'Email Institutionnel',
      forgotSending: 'Envoi en cours...',
      forgotCta: 'Envoyer le lien',
      invalidCredentials: 'Identifiants incorrects. Vérifiez votre email et mot de passe.',
      // Notification drawer
      notifTitle: 'Notifications',
      notifEmpty: 'Aucune notification',
      notifMarkAll: 'Tout marquer lu',
      notifClearRead: 'Effacer les lus',
      // Session modal
      sessionModalTitle: 'Session Expirée',
      sessionModalBody: 'Votre session a expiré. Veuillez vous reconnecter pour continuer.',
      sessionModalCta: 'Se Reconnecter',
      // Session expired page
      sessionExpiredTitle: 'Session Expirée',
      sessionExpiredBody: 'Votre session de travail a expiré par mesure de sécurité. Veuillez vous reconnecter pour continuer.',
      sessionExpiredInfo: 'Pour protéger vos données, les sessions inactives sont automatiquement fermées après 8 heures.',
      reconnectCta: 'Se Reconnecter',
      mfaSecuredLabel: 'Connexion sécurisée par authentification multi-facteurs',
    },
    parc: {
      zoneManagement: 'Gestion des Zones',
      subtitle: 'Gérez les zones du parc automobile',
      capacity: 'Capacité',
      newZone: 'Nouvelle Zone',
    },
    common: {
      loading: 'Chargement...',
      save: 'Enregistrer',
      cancel: 'Annuler',
      delete: 'Supprimer',
      edit: 'Modifier',
      create: 'Créer',
      search: 'Rechercher',
      filter: 'Filtrer',
      export: 'Exporter',
      import: 'Importer',
      actions: 'Actions',
      status: 'Statut',
      active: 'Actif',
      inactive: 'Inactif',
      close: 'Fermer',
      recordDetail: "Détail de l'enregistrement",
      fullDataView: 'Vue complète des données',
      noResults: 'Aucun résultat trouvé',
      noResultsFor: 'Aucun résultat pour',
      tryOtherTerm: 'Essayez un autre terme de recherche',
      noData: 'Aucune donnée disponible',
      view: 'Voir',
      showing: 'Affichage de',
      of: 'sur',
      results: 'résultats',
      result: 'résultat',
      new: 'Nouveau',
      searchPlaceholder: 'Rechercher...',
    },
  },
  en: {
    auth: {
      forgotTitle: 'Forgot Password',
      forgotSubtitle: 'Enter your email to reset your password',
      forgotSuccessTitle: 'Email sent!',
      forgotSuccessBody: 'If an account exists for this email, you will receive a reset link.',
      forgotSpamNote: 'Remember to check your spam folder.',
      backToLogin: 'Back to Login',
      emailInstitutionalLabel: 'Institutional Email',
      forgotSending: 'Sending...',
      forgotCta: 'Send Link',
      invalidCredentials: 'Invalid credentials. Check your email and password.',
      // Notification drawer
      notifTitle: 'Notifications',
      notifEmpty: 'No notifications',
      notifMarkAll: 'Mark all as read',
      notifClearRead: 'Clear read',
      // Session modal
      sessionModalTitle: 'Session Expired',
      sessionModalBody: 'Your session has expired. Please log in again to continue.',
      sessionModalCta: 'Log In Again',
      // Session expired page
      sessionExpiredTitle: 'Session Expired',
      sessionExpiredBody: 'Your work session has expired for security reasons. Please log in again to continue.',
      sessionExpiredInfo: 'To protect your data, inactive sessions are automatically closed after 8 hours.',
      reconnectCta: 'Reconnect',
      mfaSecuredLabel: 'Connection secured by multi-factor authentication',
    },
    parc: {
      zoneManagement: 'Zone Management',
      subtitle: 'Manage fleet park zones',
      capacity: 'Capacity',
      newZone: 'New Zone',
    },
    common: {
      loading: 'Loading...',
      save: 'Save',
      cancel: 'Cancel',
      delete: 'Delete',
      edit: 'Edit',
      create: 'Create',
      search: 'Search',
      filter: 'Filter',
      export: 'Export',
      import: 'Import',
      actions: 'Actions',
      status: 'Status',
      active: 'Active',
      inactive: 'Inactive',
      close: 'Close',
      recordDetail: 'Record Detail',
      fullDataView: 'Full Data View',
      noResults: 'No results found',
      noResultsFor: 'No results for',
      tryOtherTerm: 'Try another search term',
      noData: 'No data available',
      view: 'View',
      showing: 'Showing',
      of: 'of',
      results: 'results',
      result: 'result',
      new: 'New',
      searchPlaceholder: 'Search...',
    },
  },
} as const;

export function useI18n() {
  const { language } = useSettings();
  return translations[language] ?? translations.fr;
}
