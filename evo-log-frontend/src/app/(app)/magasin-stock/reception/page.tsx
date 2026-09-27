/**
 * Page vitrine `magasin-stock/reception`.
 * La reception MAG3 reelle est affichee dans /magasin/dashboard (receptionMag3API.getAll).
 */
import { redirect } from 'next/navigation';

export default function MagasinStockReceptionPage() {
  redirect('/magasin/dashboard');
}
