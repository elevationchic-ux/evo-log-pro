/**
 * Ancien écran « Tour de Contrôle des Corridors CEMAC » du menu
 * `transport-flotte`.
 *
 * Il ne peut pas exister tel quel : la grille de « checkpoints » frontaliers
 * (`CHECKPOINTS`) était un tableau littéralement vide, et le bouton « Radar
 * Flotte Live » affichait un message de succès sans rien rafraîchir. Le temps
 * d'attente réel par poste frontière n'est mesuré nulle part en base : aucune
 * table ne porte l'horodatage d'arrivée et de sortie d'un camion au contrôle.
 *
 * La supervision qui repose sur des données réelles  missions en cours,
 * corridors, TCO de la flotte et optimisation de tournées  est dans
 * `transport/control`, alimentée par `/transport/missions`,
 * `/transport/corridors-cemac`, `/transport/flotte/tco` et
 * `/transport/vrp-optimize`.
 */
import { redirect } from 'next/navigation';

export default function TransportFlotteControlTowerPage() {
  redirect('/transport/control');
}
