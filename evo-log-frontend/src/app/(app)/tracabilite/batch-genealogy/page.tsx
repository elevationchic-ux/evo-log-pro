'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreBatchGenealogy } from '@/components/tracabilite/registres';

export default function PageBatchGenealogy() {
  return <RegistreGenerique config={registreBatchGenealogy} />;
}
