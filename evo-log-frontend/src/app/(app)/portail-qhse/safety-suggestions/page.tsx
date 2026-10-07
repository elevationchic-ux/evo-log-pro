'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreQspSafetySuggestion } from '@/components/portail-qhse/registres_c';

export default function PageQspSafetySuggestion() {
  return <RegistreGenerique config={registreQspSafetySuggestion} />;
}
