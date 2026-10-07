'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreQhseCalibration } from '@/components/qhse-securite/registres_b';

export default function PageQhseCalibration() {
  return <RegistreGenerique config={registreQhseCalibration} />;
}
