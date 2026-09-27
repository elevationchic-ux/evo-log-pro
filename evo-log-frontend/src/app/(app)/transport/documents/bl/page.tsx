/**
 * Page `transport/documents/bl` : liste Connaissements (Bill of Lading).
 * Les BL numerises et e-POD sont a /transport/epod.
 */
import { redirect } from 'next/navigation';

export default function TransportDocumentsBlPage() {
  redirect('/transport/epod');
}
