/**
 * Page `transport/documents` : gestionnaire documentaire transport.
 * Les documents reels (e-POD, BL numerises) sont a /transport/epod.
 */
import { redirect } from 'next/navigation';

export default function TransportDocumentsPage() {
  redirect('/transport/epod');
}
