'use client';

/**
 * Marchés publics d’aménagement & contrats de PPP.
Le logiciel tient la trace des pièces (DAO, avis COLIFE ou CIP, attribution,
réceptions) : il ne conduit aucune procédure de passation, et la route de
soumission à la COLIFE le dit elle-même (501).
 *
 * Page fine : toute la mécanique (permissions granulaires, référentiels serveurs,
 * champs vides non envoyés, erreurs 409/422/501 remontées telles quelles) est
 * portée par le châssis commun RegistrePortuaire.
 */
import RegistrePortuaire from '@/components/amenagement-portuaire/RegistrePortuaire';
import { registreMarches } from '@/components/amenagement-portuaire/registres';

export default function AmenagementPortuaireMarchesPage() {
  return <RegistrePortuaire config={registreMarches} />;
}
