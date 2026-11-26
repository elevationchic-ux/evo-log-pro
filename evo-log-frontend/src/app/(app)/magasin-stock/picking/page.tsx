/**
 * Page vitrine `magasin-stock/picking`.
 * Le picking reel est a /magasin/stocks (magasinAPI.getStocks).
 */
import { redirect } from 'next/navigation';

export default function MagasinStockPickingPage() {
  redirect('/magasin/stocks');
}
