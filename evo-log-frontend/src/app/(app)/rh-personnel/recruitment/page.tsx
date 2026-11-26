'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreRecruitment } from '@/components/rh-personnel/registres';

export default function PageRecruitment() {
  return <RegistreGenerique config={registreRecruitment} />;
}
