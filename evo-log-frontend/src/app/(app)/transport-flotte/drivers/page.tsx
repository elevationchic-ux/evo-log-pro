/**
 * Ancien écran « Gestion des Chauffeurs » du menu `transport-flotte`.
 *
 * Doublon d'un écran réel : `transport/drivers` liste bien les conducteurs
 * depuis `/api/transport/chauffeurs` (nom, contact, permis & catégorie,
 * statut). Celui-ci affichait `DRIVERS_DATA`, un tableau vide, sous un
 * en-tête « Permis CEMAC / Visite Médicale / Heures Conduite / Score
 * Sécurité ».
 *
 * Sur ces quatre colonnes, trois ont une source en base (numero_permis et
 * categorie_permis, expiration_visite_medicale, la table temps_conduite
 * alimentee par POST /api/transport/temps-conduite). Une seule n'en a aucune :
 * le « Score Sécurité /100 », qui n'est calculé par aucun service 
 * l'écran réel s'arrête donc aux champs qui existent. La catégorie et la
 * visite médicale ne remontent d'ailleurs pas jusqu'au navigateur : voir la
 * note de reprise sur `ConducteurResponse`.
 */
import { redirect } from 'next/navigation';

export default function TransportFlotteDriversPage() {
  redirect('/transport/drivers');
}
