'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreConditionReading } from '@/components/maintenance-industrielle/registres';

export default function PageConditionReading() {
  return <RegistreGenerique config={registreConditionReading} />;
}
