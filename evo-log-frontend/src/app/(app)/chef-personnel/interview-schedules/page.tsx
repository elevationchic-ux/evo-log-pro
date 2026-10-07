'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreChpInterviewSchedule } from '@/components/chef-personnel/registres_c';

export default function PageChpInterviewSchedule() {
  return <RegistreGenerique config={registreChpInterviewSchedule} />;
}
