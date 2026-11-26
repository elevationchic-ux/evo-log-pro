'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreWmsKpi } from '@/components/magasin-stock/registres';

export default function PageWmsKpi() {
  return <RegistreGenerique config={registreWmsKpi} />;
}
