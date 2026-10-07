'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreChtAnnouncement } from '@/components/chat/registres_d5';

export default function PageChtAnnouncement() {
  return <RegistreGenerique config={registreChtAnnouncement} />;
}
