'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreCollAssignment } from '@/components/portail-collaborateur/registres_c';

export default function PageCollAssignment() {
  return <RegistreGenerique config={registreCollAssignment} />;
}
