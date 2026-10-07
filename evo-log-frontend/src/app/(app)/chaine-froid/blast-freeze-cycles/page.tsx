'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreCold2BlastFreezeCycle } from '@/components/chaine-froid/registres_e';

export default function PageCold2BlastFreezeCycle() {
  return <RegistreGenerique config={registreCold2BlastFreezeCycle} />;
}
