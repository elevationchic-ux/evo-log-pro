'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreProvIncident } from '@/components/annuaire-prestataires/registres_c';

export default function PageProvIncident() {
  return <RegistreGenerique config={registreProvIncident} />;
}
