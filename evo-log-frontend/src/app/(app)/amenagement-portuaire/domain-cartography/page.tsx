'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreSigLayer } from '@/components/amenagement-portuaire/registres_expansion';

export default function PageSigLayer() {
  return <RegistreGenerique config={registreSigLayer} />;
}
