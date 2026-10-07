'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreWarehouseTable } from '@/components/reports-bi/registres';

export default function PageWarehouseTable() {
  return <RegistreGenerique config={registreWarehouseTable} />;
}
