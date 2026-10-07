'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreBillingEntry } from '@/components/admin-saas/registres';

export default function PageBillingEntry() {
  return <RegistreGenerique config={registreBillingEntry} />;
}
