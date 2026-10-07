'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreAsset } from '@/components/maintenance-industrielle/registres';

export default function PageTechnicalAsset() {
  return <RegistreGenerique config={registreAsset} />;
}
