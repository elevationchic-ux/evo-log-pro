'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreCold2RefrigerantCharge } from '@/components/chaine-froid/registres_e';

export default function PageCold2RefrigerantCharge() {
  return <RegistreGenerique config={registreCold2RefrigerantCharge} />;
}
