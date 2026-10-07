'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreQualityInspection } from '@/components/magasin-stock/registres';

export default function PageQualityInspection() {
  return <RegistreGenerique config={registreQualityInspection} />;
}
