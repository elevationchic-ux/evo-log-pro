/**
 * Page vitrine du module secondaire `magasin-stock`.
 *
 * Les donnes reelles du WMS sont servies par /magasin/dashboard
 * (magasinAPI.getKpis + receptionMag3API.getAll).
 * Cette route ne fait que rediriger pour eviter un ecran vide.
 */
import { redirect } from 'next/navigation';

export default function MagasinStockDashboardPage() {
  redirect('/magasin/dashboard');
}
