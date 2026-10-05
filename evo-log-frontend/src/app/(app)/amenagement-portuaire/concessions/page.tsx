'use client';

/**
 * Concessions & contrats d’exploitation.
 * L’écart entre investissements promis et réalisés n’est pas calculé dans le
 * navigateur : la sonde « Obligations » relit /concessions/{id}/obligations et
 * affiche les agrégats du serveur, y compris leurs blanks quand rien n’est saisi.
 *
 * Page fine : toute la mécanique (permissions granulaires, référentiels serveurs,
 * champs vides non envoyés, erreurs 409/422/501 remontées telles quelles) est
 * portée par le châssis commun RegistrePortuaire.
 */
import RegistrePortuaire from '@/components/amenagement-portuaire/RegistrePortuaire';
import { registreConcessions } from '@/components/amenagement-portuaire/registres';

export default function AmenagementPortuaireConcessionsPage() {
  return <RegistrePortuaire config={registreConcessions} />;
}
