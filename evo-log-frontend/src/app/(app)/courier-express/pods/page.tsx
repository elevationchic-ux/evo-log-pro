'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registrePod } from '@/components/courier-express/registres';

export default function PageCourierPod() {
  return <RegistreGenerique config={registrePod} />;
}
