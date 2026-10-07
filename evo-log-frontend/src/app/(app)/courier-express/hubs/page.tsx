'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreHub } from '@/components/courier-express/registres';

export default function PageCourierHub() {
  return <RegistreGenerique config={registreHub} />;
}
