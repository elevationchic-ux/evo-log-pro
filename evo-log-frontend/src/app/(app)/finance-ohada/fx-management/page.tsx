'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreFxExposure } from '@/components/finance-ohada/registres';

export default function PageFxExposure() {
  return <RegistreGenerique config={registreFxExposure} />;
}
