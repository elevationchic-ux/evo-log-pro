'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreEnvironmentalMeasurement } from '@/components/qhse-securite/registres';

export default function PageEnvironmentalMeasurement() {
  return <RegistreGenerique config={registreEnvironmentalMeasurement} />;
}
