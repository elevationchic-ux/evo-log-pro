/**
 * Page `transport/containers/declaration` : formulaire de declaration en douane.
 * La declaration d'importation est geree par le module transit-douane.
 * Le suivi des conteneurs est a /transport/containers.
 */
import { redirect } from 'next/navigation';

export default function TransportContainersDeclarationPage() {
  redirect('/transport/containers');
}
