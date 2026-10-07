'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreAdmCSubscriptionPlan } from '@/components/admin-saas/registres_c';

export default function PageAdmCSubscriptionPlan() {
  return <RegistreGenerique config={registreAdmCSubscriptionPlan} />;
}
