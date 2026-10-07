'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreProvIntervention } from '@/components/annuaire-prestataires/registres_c';

export default function PageProvIntervention() {
  return <RegistreGenerique config={registreProvIntervention} />;
}
