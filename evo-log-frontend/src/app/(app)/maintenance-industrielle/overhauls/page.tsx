'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreOverhaul } from '@/components/maintenance-industrielle/registres';

export default function PageOverhaulCampaign() {
  return <RegistreGenerique config={registreOverhaul} />;
}
