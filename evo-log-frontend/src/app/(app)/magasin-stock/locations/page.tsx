/**
 * Page vitrine `magasin-stock/locations`.
 * Pas encore de endpoint locations; redirige vers le dashboard principal.
 */
import { redirect } from 'next/navigation';

export default function MagasinStockLocationsPage() {
  redirect('/magasin/dashboard');
}
