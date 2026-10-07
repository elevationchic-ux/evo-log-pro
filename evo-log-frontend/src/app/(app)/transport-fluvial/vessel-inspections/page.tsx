'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreFluvialVesselInspection } from '@/components/transport-fluvial/registres_b';

export default function PageFluvialVesselInspection() {
  return <RegistreGenerique config={registreFluvialVesselInspection} />;
}
