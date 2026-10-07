'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreEmpAttendanceCorrection } from '@/components/portail-employe/registres_c';

export default function PageEmpAttendanceCorrection() {
  return <RegistreGenerique config={registreEmpAttendanceCorrection} />;
}
