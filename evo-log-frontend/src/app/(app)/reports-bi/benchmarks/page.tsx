'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreIndustryBenchmark } from '@/components/reports-bi/registres';

export default function PageIndustryBenchmark() {
  return <RegistreGenerique config={registreIndustryBenchmark} />;
}
