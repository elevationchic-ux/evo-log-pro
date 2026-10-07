'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreEmpOvertimeRequest } from '@/components/portail-employe/registres_c';

export default function PageEmpOvertimeRequest() {
  return <RegistreGenerique config={registreEmpOvertimeRequest} />;
}
