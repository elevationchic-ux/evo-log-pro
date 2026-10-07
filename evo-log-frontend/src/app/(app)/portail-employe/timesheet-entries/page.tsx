'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreEmpTimesheetEntry } from '@/components/portail-employe/registres_c';

export default function PageEmpTimesheetEntry() {
  return <RegistreGenerique config={registreEmpTimesheetEntry} />;
}
