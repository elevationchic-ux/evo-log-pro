'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreB2bCSupportTicket } from '@/components/client-b2b/registres_c';

export default function PageB2bCSupportTicket() {
  return <RegistreGenerique config={registreB2bCSupportTicket} />;
}
