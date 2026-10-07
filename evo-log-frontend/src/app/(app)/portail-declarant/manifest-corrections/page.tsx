'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreDeclManifestCorrection } from '@/components/portail-declarant/registres_c';

export default function PageDeclManifestCorrection() {
  return <RegistreGenerique config={registreDeclManifestCorrection} />;
}
