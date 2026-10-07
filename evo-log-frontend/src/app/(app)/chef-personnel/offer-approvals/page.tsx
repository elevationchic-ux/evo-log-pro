'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreChpOfferApproval } from '@/components/chef-personnel/registres_c';

export default function PageChpOfferApproval() {
  return <RegistreGenerique config={registreChpOfferApproval} />;
}
