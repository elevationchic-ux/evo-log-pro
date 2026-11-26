'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreChpPayrollAdjustmentRequest } from '@/components/chef-personnel/registres_c';

export default function PageChpPayrollAdjustmentRequest() {
  return <RegistreGenerique config={registreChpPayrollAdjustmentRequest} />;
}
