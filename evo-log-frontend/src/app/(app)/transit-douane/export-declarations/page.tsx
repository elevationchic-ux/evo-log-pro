'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreExportDeclaration } from '@/components/transit-douane/registres';

export default function PageExportDeclaration() {
  return <RegistreGenerique config={registreExportDeclaration} />;
}
