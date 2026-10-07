'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreUsageAnalytics } from '@/components/admin-saas/registres';

export default function PageUsageAnalytics() {
  return <RegistreGenerique config={registreUsageAnalytics} />;
}
