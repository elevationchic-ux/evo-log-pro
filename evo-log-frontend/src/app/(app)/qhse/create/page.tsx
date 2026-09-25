// Page « créer » QHSE : l'ancien placeholder développeur (« Create page for
// qhse ») est remplacé par une redirection vers le formulaire réel du module.
import { redirect } from 'next/navigation';

export default function CreatePage() {
  redirect('/qhse/edit');
}
