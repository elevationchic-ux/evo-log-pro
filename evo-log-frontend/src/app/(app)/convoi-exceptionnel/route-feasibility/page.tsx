'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreHeavy2RouteSurvey } from '@/components/convoi-exceptionnel/registres_e';

export default function PageHeavy2RouteSurvey() {
  return <RegistreGenerique config={registreHeavy2RouteSurvey} />;
}
