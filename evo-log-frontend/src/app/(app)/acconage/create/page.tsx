// Page « créer » Acconage : l'ancien placeholder développeur (« Create page
// for acconage ») est remplacé par une redirection vers le formulaire réel.
import { redirect } from 'next/navigation';

export default function CreatePage() {
  redirect('/acconage/edit');
}
