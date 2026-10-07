'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreAccessReview } from '@/components/superadmin-cadc/registres';

export default function PageAccessReview() {
  return <RegistreGenerique config={registreAccessReview} />;
}
