'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreHeavy2AxleLoadReading } from '@/components/convoi-exceptionnel/registres_e';

export default function PageHeavy2AxleLoadReading() {
  return <RegistreGenerique config={registreHeavy2AxleLoadReading} />;
}
