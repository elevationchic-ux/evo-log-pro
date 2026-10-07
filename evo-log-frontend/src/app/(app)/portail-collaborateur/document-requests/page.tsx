'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreCollDocumentRequest } from '@/components/portail-collaborateur/registres_c';

export default function PageCollDocumentRequest() {
  return <RegistreGenerique config={registreCollDocumentRequest} />;
}
