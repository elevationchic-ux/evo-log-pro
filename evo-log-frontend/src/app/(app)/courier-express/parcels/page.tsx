'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreParcel } from '@/components/courier-express/registres';

export default function PageCourierParcel() {
  return <RegistreGenerique config={registreParcel} />;
}
