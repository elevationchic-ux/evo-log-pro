'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreCold2TemperatureLog } from '@/components/chaine-froid/registres_e';

export default function PageCold2TemperatureLog() {
  return <RegistreGenerique config={registreCold2TemperatureLog} />;
}
