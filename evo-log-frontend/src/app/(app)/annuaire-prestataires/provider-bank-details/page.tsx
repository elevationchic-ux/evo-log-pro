'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreProvBankDetail } from '@/components/annuaire-prestataires/registres_c';

export default function PageProvBankDetail() {
  return <RegistreGenerique config={registreProvBankDetail} />;
}
