'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreUptimeRecord } from '@/components/admin-saas/registres';

export default function PageUptimeRecord() {
  return <RegistreGenerique config={registreUptimeRecord} />;
}
