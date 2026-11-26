/**
 * Réglages du contrôle carburant (FuelGuard), partagés par la page de saisie
 * des tickets et par le tableau de bord : un seul point de vérité pour le
 * seuil de surveillance et pour le prix pré-rempli à la saisie.
 *
 * Ces deux valeurs sont des paramètres métier, pas des données affichées : le
 * prix pré-rempli reste modifiable par l'opérateur et n'est jamais facturé en
 * l'état sans saisie réelle.
 */

/**
 * Seuil de surveillance d'un poids lourd, en L/100 km. Au-delà, le plein est
 * signalé pour investigation (siphonnage, capteur, style de conduite).
 */
export const SEUIL_SURCONSOMMATION_L100 = 45;

/** Prix officiel du gazole au Cameroun (XAF / litre), proposé par défaut. */
export const PRIX_GAZOLE_XAF = 828;
