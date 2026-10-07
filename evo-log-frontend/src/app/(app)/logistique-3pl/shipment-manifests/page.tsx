'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreTplShipmentManifest } from '@/components/logistique-3pl/registres_b';

export default function PageTplShipmentManifest() {
  return <RegistreGenerique config={registreTplShipmentManifest} />;
}
