/**
 * Page vitrine `magasin-stock/locations`.
 * Les emplacements/slots reels sont a /magasin/wms-slots.
 */
import { redirect } from 'next/navigation';

export default function MagasinStockLocationsPage() {
  redirect('/magasin/wms-slots');
}
