'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registrePredictiveModel } from '@/components/reports-bi/registres';

export default function PagePredictiveModel() {
  return <RegistreGenerique config={registrePredictiveModel} />;
}
