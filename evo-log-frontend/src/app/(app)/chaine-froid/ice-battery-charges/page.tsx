'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreCold2IceBatteryCharge } from '@/components/chaine-froid/registres_e';

export default function PageCold2IceBatteryCharge() {
  return <RegistreGenerique config={registreCold2IceBatteryCharge} />;
}
