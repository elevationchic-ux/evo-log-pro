/**
 * Page `transport/dispatch` : dispatch par vehicule.
 * Le suivi dispatch reel est a /transport/control (missions, corridors, TCO).
 * Cette route etait une coquille vide (fleet = []) sans appel API.
 */
import { redirect } from 'next/navigation';

export default function TransportDispatchPage() {
  redirect('/transport/control');
}
