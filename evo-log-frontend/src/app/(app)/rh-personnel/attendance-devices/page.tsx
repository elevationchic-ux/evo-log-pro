'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreAttendanceDevice } from '@/components/rh-personnel/registres';

export default function PageAttendanceDevice() {
  return <RegistreGenerique config={registreAttendanceDevice} />;
}
