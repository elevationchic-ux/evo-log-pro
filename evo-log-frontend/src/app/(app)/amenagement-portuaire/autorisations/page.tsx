'use client';

/**
 * Autorisations administratives & études d’impact (EIES, permis).
 * Les natures et statuts proposés viennent de /nomenclatures. Le dépôt auprès du
 * guichet environnemental officiel n’est pas simulé : la route l’annonce (501),
 * la page affiche le message du serveur tel quel.
 *
 * Page fine : toute la mécanique (permissions granulaires, référentiels serveurs,
 * champs vides non envoyés, erreurs 409/422/501 remontées telles quelles) est
 * portée par le châssis commun RegistrePortuaire.
 */
import RegistrePortuaire from '@/components/amenagement-portuaire/RegistrePortuaire';
import { registreAutorisations } from '@/components/amenagement-portuaire/registres';

export default function AmenagementPortuaireAutorisationsPage() {
  return <RegistrePortuaire config={registreAutorisations} />;
}
