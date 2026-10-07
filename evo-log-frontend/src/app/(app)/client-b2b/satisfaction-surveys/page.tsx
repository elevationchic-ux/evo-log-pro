'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreSatisfactionSurvey } from '@/components/client-b2b/registres';

export default function PageSatisfactionSurvey() {
  return <RegistreGenerique config={registreSatisfactionSurvey} />;
}
