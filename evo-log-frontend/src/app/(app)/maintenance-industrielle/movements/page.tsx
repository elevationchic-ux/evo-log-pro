'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreMovement } from '@/components/maintenance-industrielle/registres';

export default function PagePartMovement() {
  return <RegistreGenerique config={registreMovement} />;
}
