'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreCollShiftAttendance } from '@/components/portail-collaborateur/registres_c';

export default function PageCollShiftAttendance() {
  return <RegistreGenerique config={registreCollShiftAttendance} />;
}
