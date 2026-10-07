'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreSensor } from '@/components/maintenance-industrielle/registres';

export default function PageSensor() {
  return <RegistreGenerique config={registreSensor} />;
}
