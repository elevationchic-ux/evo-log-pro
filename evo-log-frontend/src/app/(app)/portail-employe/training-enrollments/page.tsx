'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreEmpTrainingEnrollment } from '@/components/portail-employe/registres_c';

export default function PageEmpTrainingEnrollment() {
  return <RegistreGenerique config={registreEmpTrainingEnrollment} />;
}
