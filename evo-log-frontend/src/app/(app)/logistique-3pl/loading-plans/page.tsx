'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreTplLoadingPlan } from '@/components/logistique-3pl/registres_b';

export default function PageTplLoadingPlan() {
  return <RegistreGenerique config={registreTplLoadingPlan} />;
}
