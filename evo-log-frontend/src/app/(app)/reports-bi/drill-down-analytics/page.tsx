'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreDrillPath } from '@/components/reports-bi/registres';

export default function PageDrillPath() {
  return <RegistreGenerique config={registreDrillPath} />;
}
