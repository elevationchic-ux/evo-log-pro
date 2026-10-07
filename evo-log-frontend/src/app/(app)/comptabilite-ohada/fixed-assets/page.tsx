'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreAssetRegistration } from '@/components/comptabilite-ohada/registres';

export default function PageAssetRegistration() {
  return <RegistreGenerique config={registreAssetRegistration} />;
}
