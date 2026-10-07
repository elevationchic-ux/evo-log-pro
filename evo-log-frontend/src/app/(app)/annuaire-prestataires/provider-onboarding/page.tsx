'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreProvOnboarding } from '@/components/annuaire-prestataires/registres_c';

export default function PageProvOnboarding() {
  return <RegistreGenerique config={registreProvOnboarding} />;
}
