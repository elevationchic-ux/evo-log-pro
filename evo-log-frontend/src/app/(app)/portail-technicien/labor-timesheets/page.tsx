'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreTechLaborTimesheet } from '@/components/portail-technicien/registres_c';

export default function PageTechLaborTimesheet() {
  return <RegistreGenerique config={registreTechLaborTimesheet} />;
}
