'use client';

/**
 * Inventaire technique des infrastructures aménagées.
Aucune note de génie civil n’est déduite : elle provient d’un rapport
d’expertise consigné par l’action dédiée. Une sortie d’inventaire exige un
motif, la route DELETE du serveur le refusant sinon.
 *
 * Page fine : toute la mécanique (permissions granulaires, référentiels serveurs,
 * champs vides non envoyés, erreurs 409/422/501 remontées telles quelles) est
 * portée par le châssis commun RegistrePortuaire.
 */
import RegistrePortuaire from '@/components/amenagement-portuaire/RegistrePortuaire';
import { registreInfrastructures } from '@/components/amenagement-portuaire/registres';

export default function AmenagementPortuaireInfrastructuresPage() {
  return <RegistrePortuaire config={registreInfrastructures} />;
}
