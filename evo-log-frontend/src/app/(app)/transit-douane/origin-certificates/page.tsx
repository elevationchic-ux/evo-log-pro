'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreOriginCertificate } from '@/components/transit-douane/registres';

export default function PageOriginCertificate() {
  return <RegistreGenerique config={registreOriginCertificate} />;
}
