'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreChpOnboardingChecklist } from '@/components/chef-personnel/registres_c';

export default function PageChpOnboardingChecklist() {
  return <RegistreGenerique config={registreChpOnboardingChecklist} />;
}
