'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreProvProfile } from '@/components/annuaire-prestataires/registres_c';

export default function PageProvProfile() {
  return <RegistreGenerique config={registreProvProfile} />;
}
