'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreParcInspectionChecklist } from '@/components/parc-vehicules/registres_b';

export default function PageParcInspectionChecklist() {
  return <RegistreGenerique config={registreParcInspectionChecklist} />;
}
