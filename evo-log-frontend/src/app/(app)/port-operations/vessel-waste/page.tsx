'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreVesselWasteReceipt } from '@/components/port-operations/registres';

export default function PageVesselWasteReceipt() {
  return <RegistreGenerique config={registreVesselWasteReceipt} />;
}
