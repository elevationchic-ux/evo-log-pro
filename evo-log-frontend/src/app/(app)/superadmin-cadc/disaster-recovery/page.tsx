'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreDrPlan } from '@/components/superadmin-cadc/registres';

export default function PageDrPlan() {
  return <RegistreGenerique config={registreDrPlan} />;
}
