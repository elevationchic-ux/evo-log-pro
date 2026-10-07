'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreMagcDockAssignment } from '@/components/portail-magasinier/registres_c';

export default function PageMagcDockAssignment() {
  return <RegistreGenerique config={registreMagcDockAssignment} />;
}
