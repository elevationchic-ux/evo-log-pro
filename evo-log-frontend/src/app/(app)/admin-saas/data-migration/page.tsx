'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreDataMigration } from '@/components/admin-saas/registres';

export default function PageDataMigration() {
  return <RegistreGenerique config={registreDataMigration} />;
}
