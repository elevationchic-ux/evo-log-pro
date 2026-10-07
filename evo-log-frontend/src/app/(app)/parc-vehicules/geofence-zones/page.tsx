'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreParcGeofenceZone } from '@/components/parc-vehicules/registres_b';

export default function PageParcGeofenceZone() {
  return <RegistreGenerique config={registreParcGeofenceZone} />;
}
