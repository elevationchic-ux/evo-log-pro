'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreScorecard } from '@/components/reports-bi/registres';

export default function PageScorecard() {
  return <RegistreGenerique config={registreScorecard} />;
}
