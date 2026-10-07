'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreHrReport } from '@/components/rh-personnel/registres';

export default function PageHrReport() {
  return <RegistreGenerique config={registreHrReport} />;
}
