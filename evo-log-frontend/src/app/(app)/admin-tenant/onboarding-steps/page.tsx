'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreAdmtOnboardingStep } from '@/components/admin-tenant/registres_c';

export default function PageAdmtOnboardingStep() {
  return <RegistreGenerique config={registreAdmtOnboardingStep} />;
}
