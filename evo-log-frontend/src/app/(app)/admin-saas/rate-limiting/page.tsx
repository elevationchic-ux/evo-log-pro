'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreApiQuota } from '@/components/admin-saas/registres';

export default function PageApiQuota() {
  return <RegistreGenerique config={registreApiQuota} />;
}
