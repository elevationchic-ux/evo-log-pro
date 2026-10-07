'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreCourier } from '@/components/courier-express/registres';

export default function PageCourierCourier() {
  return <RegistreGenerique config={registreCourier} />;
}
