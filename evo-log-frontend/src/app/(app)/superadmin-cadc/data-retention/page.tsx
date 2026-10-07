'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreRetentionPolicy } from '@/components/superadmin-cadc/registres';

export default function PageRetentionPolicy() {
  return <RegistreGenerique config={registreRetentionPolicy} />;
}
