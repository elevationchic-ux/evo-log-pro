'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreAssetFailure } from '@/components/maintenance-industrielle/registres';

export default function PageAssetFailure() {
  return <RegistreGenerique config={registreAssetFailure} />;
}
