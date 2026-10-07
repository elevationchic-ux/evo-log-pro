'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreDangerousGoodsLoad } from '@/components/transport-flotte/registres';

export default function PageDangerousGoodsLoad() {
  return <RegistreGenerique config={registreDangerousGoodsLoad} />;
}
