'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreMagcGoodsIssue } from '@/components/portail-magasinier/registres_c';

export default function PageMagcGoodsIssue() {
  return <RegistreGenerique config={registreMagcGoodsIssue} />;
}
