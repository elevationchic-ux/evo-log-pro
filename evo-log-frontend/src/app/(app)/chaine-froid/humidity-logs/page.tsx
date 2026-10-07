'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreCold2HumidityLog } from '@/components/chaine-froid/registres_e';

export default function PageCold2HumidityLog() {
  return <RegistreGenerique config={registreCold2HumidityLog} />;
}
