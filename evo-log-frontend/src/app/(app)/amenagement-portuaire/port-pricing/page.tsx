'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registrePortPerception } from '@/components/amenagement-portuaire/registres_expansion';

export default function PagePortPerception() {
  return <RegistreGenerique config={registrePortPerception} />;
}
