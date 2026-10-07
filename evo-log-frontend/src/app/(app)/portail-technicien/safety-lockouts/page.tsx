'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreTechSafetyLockout } from '@/components/portail-technicien/registres_c';

export default function PageTechSafetyLockout() {
  return <RegistreGenerique config={registreTechSafetyLockout} />;
}
