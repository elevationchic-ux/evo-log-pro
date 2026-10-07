'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreMagcPalletBuild } from '@/components/portail-magasinier/registres_c';

export default function PageMagcPalletBuild() {
  return <RegistreGenerique config={registreMagcPalletBuild} />;
}
