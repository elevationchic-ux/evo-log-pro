'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreParcDriverAssignment } from '@/components/parc-vehicules/registres_b';

export default function PageParcDriverAssignment() {
  return <RegistreGenerique config={registreParcDriverAssignment} />;
}
