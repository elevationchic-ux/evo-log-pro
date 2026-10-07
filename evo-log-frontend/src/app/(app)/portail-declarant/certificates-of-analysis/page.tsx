'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreDeclCertificateAnalysis } from '@/components/portail-declarant/registres_c';

export default function PageDeclCertificateAnalysis() {
  return <RegistreGenerique config={registreDeclCertificateAnalysis} />;
}
