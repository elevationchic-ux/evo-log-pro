'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreEmpSelfReview } from '@/components/portail-employe/registres_c';

export default function PageEmpSelfReview() {
  return <RegistreGenerique config={registreEmpSelfReview} />;
}
