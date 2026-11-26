/**
 * Page d'entrée du département Aménagement portuaire & Domaine public.
 *
 * Le point d'entrée réel est le centre de pilotage (/amenagement-portuaire/
 * dashboard), celui que déclare le registre de navigation : cette page ne
 * duplique aucun écran, elle redirige, pour que /amenagement-portuaire ne
 * tombe jamais sur un 404 quand un agent saisit le préfixe du département.
 */
import { redirect } from 'next/navigation';

export default function AmenagementPortuaireIndexPage() {
  redirect('/amenagement-portuaire/dashboard');
}
