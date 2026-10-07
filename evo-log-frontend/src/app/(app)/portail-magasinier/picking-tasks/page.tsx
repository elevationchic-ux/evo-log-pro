'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreMagcPickingTask } from '@/components/portail-magasinier/registres_c';

export default function PageMagcPickingTask() {
  return <RegistreGenerique config={registreMagcPickingTask} />;
}
