'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreSaCMigrationRun } from '@/components/superadmin-cadc/registres_c';

export default function PageSaCMigrationRun() {
  return <RegistreGenerique config={registreSaCMigrationRun} />;
}
