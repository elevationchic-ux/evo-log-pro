'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreProvReview } from '@/components/annuaire-prestataires/registres_c';

export default function PageProvReview() {
  return <RegistreGenerique config={registreProvReview} />;
}
