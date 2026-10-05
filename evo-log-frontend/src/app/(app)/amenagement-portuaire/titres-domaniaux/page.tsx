'use client';

/**
 * Titres domaniaux & occupations du domaine public.
Une décision (accord ou refus motivé) est enregistrée avec son autorité et sa
date réelles. Un titre n’est jamais effacé : abrogé, annulé ou échu, il reste
au registre, qui fait foi.
 *
 * Page fine : toute la mécanique (permissions granulaires, référentiels serveurs,
 * champs vides non envoyés, erreurs 409/422/501 remontées telles quelles) est
 * portée par le châssis commun RegistrePortuaire.
 */
import RegistrePortuaire from '@/components/amenagement-portuaire/RegistrePortuaire';
import { registreTitres } from '@/components/amenagement-portuaire/registres';

export default function AmenagementPortuaireTitresDomaniauxPage() {
  return <RegistrePortuaire config={registreTitres} />;
}
