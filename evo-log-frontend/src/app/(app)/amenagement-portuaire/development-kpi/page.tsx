'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreAmenagementKpi } from '@/components/amenagement-portuaire/registres_expansion';

export default function PageAmenagementKpi() {
  return <RegistreGenerique config={registreAmenagementKpi} />;
}
