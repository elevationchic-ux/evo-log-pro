'use client';

/**
 * Chaîne de programmation des projets (fiche technique, PIP/CDMT, engagement).
 * Les états affichés viennent de la nomenclature « statut_document_programmation »
 * servie par /nomenclatures : la page n’en fixe aucun. Les visas (maturité,
 * contrôle financier) sont consignés comme actes pris par l’administration.
 *
 * Page fine : toute la mécanique (permissions granulaires, référentiels serveurs,
 * champs vides non envoyés, erreurs 409/422/501 remontées telles quelles) est
 * portée par le châssis commun RegistrePortuaire.
 */
import RegistrePortuaire from '@/components/amenagement-portuaire/RegistrePortuaire';
import { registreProgrammation } from '@/components/amenagement-portuaire/registres';

export default function AmenagementPortuaireProgrammationPage() {
  return <RegistrePortuaire config={registreProgrammation} />;
}
