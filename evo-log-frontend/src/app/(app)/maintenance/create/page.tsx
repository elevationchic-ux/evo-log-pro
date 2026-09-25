// Page « créer » Maintenance : l'ancien placeholder développeur (« Create
// page for maintenance ») est remplacé par une redirection vers le formulaire réel.
import { redirect } from 'next/navigation';

export default function CreatePage() {
  redirect('/maintenance/edit');
}
