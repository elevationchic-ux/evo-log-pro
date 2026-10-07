'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreChpRecruitmentCampaign } from '@/components/chef-personnel/registres_c';

export default function PageChpRecruitmentCampaign() {
  return <RegistreGenerique config={registreChpRecruitmentCampaign} />;
}
