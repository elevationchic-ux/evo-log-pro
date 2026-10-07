'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreCold2ColdExcursion } from '@/components/chaine-froid/registres_e';

export default function PageCold2ColdExcursion() {
  return <RegistreGenerique config={registreCold2ColdExcursion} />;
}
