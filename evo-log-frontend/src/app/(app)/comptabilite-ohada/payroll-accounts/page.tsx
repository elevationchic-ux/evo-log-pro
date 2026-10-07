'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registrePayrollEntry } from '@/components/comptabilite-ohada/registres';

export default function PagePayrollEntry() {
  return <RegistreGenerique config={registrePayrollEntry} />;
}
