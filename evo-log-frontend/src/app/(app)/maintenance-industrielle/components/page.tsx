'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreComponent } from '@/components/maintenance-industrielle/registres';

export default function PageAssetComponent() {
  return <RegistreGenerique config={registreComponent} />;
}
