'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreClientOnboarding } from '@/components/client-b2b/registres';

export default function PageClientOnboarding() {
  return <RegistreGenerique config={registreClientOnboarding} />;
}
