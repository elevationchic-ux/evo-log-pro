'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registrePerformanceReview } from '@/components/rh-personnel/registres';

export default function PagePerformanceReview() {
  return <RegistreGenerique config={registrePerformanceReview} />;
}
