/**
 * Ancien écran « Télématique Carburant & Anti-Siphonnage » du menu
 * `transport-flotte`.
 *
 * Il ne peut pas exister tel quel : il affichait des niveaux de cuve, des sonde
 * CanBus et des alertes de siphonnage pour lesquels aucune table n'existe en
 * base, tout en certifiant « conforme aux standards constructeurs » au-dessus
 * d'un tableau vide. Le carburant réellement mesuré est alimenté par les
 * tickets saisis par les conducteurs : le tableau de bord `transport/fuel` et
 * l'historique par véhicule `transport/fuel/history` répondent aux mêmes
 * questions, sur des données réelles.
 */
import { redirect } from 'next/navigation';

export default function TransportFlotteFuelTelematicsPage() {
  redirect('/transport/fuel');
}
