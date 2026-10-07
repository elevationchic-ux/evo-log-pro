'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreFailureMode } from '@/components/maintenance-industrielle/registres';

export default function PageFailureMode() {
  return <RegistreGenerique config={registreFailureMode} />;
}
