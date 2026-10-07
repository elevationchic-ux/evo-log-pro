'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreProvBlacklist } from '@/components/annuaire-prestataires/registres_c';

export default function PageProvBlacklist() {
  return <RegistreGenerique config={registreProvBlacklist} />;
}
