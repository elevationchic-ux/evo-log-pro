'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreServiceRequest } from '@/components/client-b2b/registres';

export default function PageServiceRequest() {
  return <RegistreGenerique config={registreServiceRequest} />;
}
