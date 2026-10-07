'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreTplSlaKpi } from '@/components/logistique-3pl/registres';

export default function PageTplSlaKpi() {
  return <RegistreGenerique config={registreTplSlaKpi} />;
}
