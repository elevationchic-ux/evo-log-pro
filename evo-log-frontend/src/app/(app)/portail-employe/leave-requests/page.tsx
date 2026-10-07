'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreEmpLeaveRequest } from '@/components/portail-employe/registres_c';

export default function PageEmpLeaveRequest() {
  return <RegistreGenerique config={registreEmpLeaveRequest} />;
}
