'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreWaybill } from '@/components/courier-express/registres';

export default function PageCourierWaybill() {
  return <RegistreGenerique config={registreWaybill} />;
}
