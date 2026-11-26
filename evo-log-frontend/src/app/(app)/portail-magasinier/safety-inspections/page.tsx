'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreMagcSafetyInspection } from '@/components/portail-magasinier/registres_c';

export default function PageMagcSafetyInspection() {
  return <RegistreGenerique config={registreMagcSafetyInspection} />;
}
