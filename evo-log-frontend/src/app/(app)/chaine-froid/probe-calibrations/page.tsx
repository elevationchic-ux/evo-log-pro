'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreCold2ProbeCalibration } from '@/components/chaine-froid/registres_e';

export default function PageCold2ProbeCalibration() {
  return <RegistreGenerique config={registreCold2ProbeCalibration} />;
}
