'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreDeclDutyReliefClaim } from '@/components/portail-declarant/registres_c';

export default function PageDeclDutyReliefClaim() {
  return <RegistreGenerique config={registreDeclDutyReliefClaim} />;
}
