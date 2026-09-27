/**
 * Page vitrine `magasin-stock/movements`.
 * Les mouvements/transferts reels sont a /magasin/transactions (apiClient).
 */
import { redirect } from 'next/navigation';

export default function MagasinStockMovementsPage() {
  redirect('/magasin/transactions');
}
