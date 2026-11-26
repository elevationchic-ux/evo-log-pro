/**
 * Ancien écran « Missions & Dispatch Intelligent » du menu `transport-flotte`.
 *
 * Écran mort : il parcourait `MISSIONS`, un tableau littéralement vide, sous
 * des bandeaux « Taux d'Utilisation Flotte », « Ponctualité (OTD) » et
 * « Alertes Géolocalisation  arrêts prolongés ».
 *
 * Ce n'est pas un manque de données qui justifie la suppression : les
 * sources existent (`/api/transport/missions`, `/api/transport/gps` sur la
 * table position_gps, heure_arrivee_prevue / heure_arrivee_reelle du trajet).
 * C'est que le travail est déjà fait, et bien fait, ailleurs :
 * `transport/missions` pour la liste et le statut des missions,
 * `transport/control` pour la tour de contrôle, `/transport/planning` pour la
 * planification. Deux écrans sur le même objet = deux sources de vérité qui
 * se contredisent.
 */
import { redirect } from 'next/navigation';

export default function TransportFlotteMissionsDispatchPage() {
  redirect('/transport/missions');
}
