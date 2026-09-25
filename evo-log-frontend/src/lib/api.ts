/**
 * Shim de compatibilité  NE PAS UTILISER DANS DU NOUVEAU CODE.
 *
 * L'unique client API du projet est `@/lib/api-client` (apiClient + services typés).
 * Cet ancien instance axios (avec son propre token localStorage et sa réécriture /api/v1)
 * est redirigé vers le client unifié pour garantir une seule comportement d'auth,
 * de refresh et de normalisation d'URL dans toute l'application.
 */
export { apiClient as default } from './api-client';
export { apiClient } from './api-client';
