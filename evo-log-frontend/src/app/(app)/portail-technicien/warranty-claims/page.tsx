'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreTechWarrantyClaim } from '@/components/portail-technicien/registres_c';

export default function PageTechWarrantyClaim() {
  return <RegistreGenerique config={registreTechWarrantyClaim} />;
}
