'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreAirDangerousGoods } from '@/components/transport-aerien/registres';

export default function PageAirDangerousGoods() {
  return <RegistreGenerique config={registreAirDangerousGoods} />;
}
