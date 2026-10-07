'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreAdmtFeatureEntitlement } from '@/components/admin-tenant/registres_c';

export default function PageAdmtFeatureEntitlement() {
  return <RegistreGenerique config={registreAdmtFeatureEntitlement} />;
}
