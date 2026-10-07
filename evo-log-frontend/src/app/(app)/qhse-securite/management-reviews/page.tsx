'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreManagementReview } from '@/components/qhse-securite/registres';

export default function PageManagementReview() {
  return <RegistreGenerique config={registreManagementReview} />;
}
