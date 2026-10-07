'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreVehiculeEx } from '@/components/courier-express/registres';

export default function PageCourierVehicule() {
  return <RegistreGenerique config={registreVehiculeEx} />;
}
