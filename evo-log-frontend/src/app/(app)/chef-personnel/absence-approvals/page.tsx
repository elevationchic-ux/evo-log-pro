'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreChpAbsenceApproval } from '@/components/chef-personnel/registres_c';

export default function PageChpAbsenceApproval() {
  return <RegistreGenerique config={registreChpAbsenceApproval} />;
}
