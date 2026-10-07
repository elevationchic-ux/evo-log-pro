'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreVendor } from '@/components/maintenance-industrielle/registres';

export default function PageMaintenanceVendor() {
  return <RegistreGenerique config={registreVendor} />;
}
