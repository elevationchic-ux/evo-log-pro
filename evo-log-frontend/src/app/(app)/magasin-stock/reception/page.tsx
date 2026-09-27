/**
 * Page vitrine `magasin-stock/reception`.
 * La reception MAG3 reelle est a /magasin/reception-mag3 (receptionMag3API).
 */
import { redirect } from 'next/navigation';

export default function MagasinStockReceptionPage() {
  redirect('/magasin/reception-mag3');
}
