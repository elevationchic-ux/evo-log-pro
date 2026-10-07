'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreTransitbInspectionRecord } from '@/components/transit-douane/registres_b';

export default function PageTransitbInspectionRecord() {
  return <RegistreGenerique config={registreTransitbInspectionRecord} />;
}
