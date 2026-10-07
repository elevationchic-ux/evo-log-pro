'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreHLBallast } from '@/components/convoi-exceptionnel/registres';

export default function PageHeavyLiftBallast() {
  return <RegistreGenerique config={registreHLBallast} />;
}
