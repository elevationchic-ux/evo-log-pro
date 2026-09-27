/**
 * Page vitrine `magasin-stock/inventory`.
 * L'inventaire reel est a /magasin/inventory (magasinAPI.getStocks).
 */
import { redirect } from 'next/navigation';

export default function MagasinStockInventoryPage() {
  redirect('/magasin/inventory');
}
