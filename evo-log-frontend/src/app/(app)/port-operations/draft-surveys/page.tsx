'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreDraftSurvey } from '@/components/port-operations/registres';

export default function PageDraftSurvey() {
  return <RegistreGenerique config={registreDraftSurvey} />;
}
