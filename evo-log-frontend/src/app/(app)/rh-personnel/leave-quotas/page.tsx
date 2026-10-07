'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreLeaveQuota } from '@/components/rh-personnel/registres';

export default function PageLeaveQuota() {
  return <RegistreGenerique config={registreLeaveQuota} />;
}
