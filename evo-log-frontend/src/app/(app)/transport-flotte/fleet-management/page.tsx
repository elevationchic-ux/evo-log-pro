/**
 * Ancien écran « Flotte Camions & Tracteurs » du menu `transport-flotte`.
 *
 * Doublon d'un écran réel : `transport/flotte` liste les véhicules depuis
 * `/api/v1/transport/camions` et `/api/v1/transport/kpis`, et permet d'en
 * déclarer. Celui-ci affichait `FLEET_DATA`, un tableau vide.
 *
 * Deux de ses colonnes n'ont en plus aucune source en base : le modèle
 * `Camion` porte bien immatriculation, marque, modèle, kilométrage et
 * échéance de maintenance, mais ni « Visite Technique » ni « Assurance » 
 * ces deux champs n'existent dans aucune table. Les faire apparaitre aurait
 * voulu dire les inventer. Le TCO, lui, est réel
 * (`/api/transport/flotte/tco`).
 */
import { redirect } from 'next/navigation';

export default function TransportFlotteFleetManagementPage() {
  redirect('/transport/flotte');
}
