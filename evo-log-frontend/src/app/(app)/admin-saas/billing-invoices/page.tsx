'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreAdmCBillingInvoice } from '@/components/admin-saas/registres_c';

export default function PageAdmCBillingInvoice() {
  return <RegistreGenerique config={registreAdmCBillingInvoice} />;
}
