'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreDocHash } from '@/components/tracabilite/registres';

export default function PageDocumentHash() {
  return <RegistreGenerique config={registreDocHash} />;
}
