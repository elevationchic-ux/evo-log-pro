'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreLocker } from '@/components/courier-express/registres';

export default function PageCourierLocker() {
  return <RegistreGenerique config={registreLocker} />;
}
