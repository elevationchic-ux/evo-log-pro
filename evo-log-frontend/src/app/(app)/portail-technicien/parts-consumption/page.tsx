'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreTechPartConsumption } from '@/components/portail-technicien/registres_c';

export default function PageTechPartConsumption() {
  return <RegistreGenerique config={registreTechPartConsumption} />;
}
