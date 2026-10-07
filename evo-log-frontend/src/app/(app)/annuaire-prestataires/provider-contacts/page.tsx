'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreProvContact } from '@/components/annuaire-prestataires/registres_c';

export default function PageProvContact() {
  return <RegistreGenerique config={registreProvContact} />;
}
