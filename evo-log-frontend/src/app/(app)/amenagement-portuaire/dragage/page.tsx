'use client';

/**
 * Campagnes de dragage & profondeurs du chenal.
 * Volumes mesuré et facturé restent deux colonnes distinctes : la réconciliation
 * appartient au décompte de l’ingénieur. Le statut est une saisie libre, le
 * serveur ne publie pas de vocabulaire pour cette colonne.
 *
 * Page fine : toute la mécanique (permissions granulaires, référentiels serveurs,
 * champs vides non envoyés, erreurs 409/422/501 remontées telles quelles) est
 * portée par le châssis commun RegistrePortuaire.
 */
import RegistrePortuaire from '@/components/amenagement-portuaire/RegistrePortuaire';
import { registreDragage } from '@/components/amenagement-portuaire/registres';

export default function AmenagementPortuaireDragagePage() {
  return <RegistrePortuaire config={registreDragage} />;
}
