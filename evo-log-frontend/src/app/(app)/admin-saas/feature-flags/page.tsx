'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreFeatureFlag } from '@/components/admin-saas/registres';

export default function PageFeatureFlag() {
  return <RegistreGenerique config={registreFeatureFlag} />;
}
