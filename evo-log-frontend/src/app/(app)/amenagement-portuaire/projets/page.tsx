'use client';

/**
 * Portefeuille des projets d'aménagement du domaine portuaire.
 *
 * Aucune ligne ni aucun pourcentage n'est produit ici : le châssis commun lit
 * /projets et n'envoie que les champs réellement saisis (le backend laisse les
 * autres NULL). La sortie du portefeuille passe par l'action « Sortir du
 * portefeuille », le serveur exigeant un motif écrit.
 */
import RegistrePortuaire from '@/components/amenagement-portuaire/RegistrePortuaire';
import { registreProjets } from '@/components/amenagement-portuaire/registres';

export default function AmenagementPortuaireProjetsPage() {
  return <RegistrePortuaire config={registreProjets} />;
}
