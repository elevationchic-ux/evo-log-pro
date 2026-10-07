'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreSaasRevenueRecord } from '@/components/superadmin-cadc/registres';

export default function PageSaasRevenueRecord() {
  return <RegistreGenerique config={registreSaasRevenueRecord} />;
}
