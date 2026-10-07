'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreSaCAuditLogReview } from '@/components/superadmin-cadc/registres_c';

export default function PageSaCAuditLogReview() {
  return <RegistreGenerique config={registreSaCAuditLogReview} />;
}
