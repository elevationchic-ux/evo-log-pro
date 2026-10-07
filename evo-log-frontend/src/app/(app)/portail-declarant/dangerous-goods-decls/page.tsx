'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreDeclDangerousGoods } from '@/components/portail-declarant/registres_c';

export default function PageDeclDangerousGoods() {
  return <RegistreGenerique config={registreDeclDangerousGoods} />;
}
