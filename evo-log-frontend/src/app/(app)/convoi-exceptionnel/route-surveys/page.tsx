'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreHLSurvey } from '@/components/convoi-exceptionnel/registres';

export default function PageHeavyLiftRouteSurvey() {
  return <RegistreGenerique config={registreHLSurvey} />;
}
