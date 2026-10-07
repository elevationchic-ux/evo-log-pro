'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreWoTool } from '@/components/maintenance-industrielle/registres';

export default function PageWorkOrderTool() {
  return <RegistreGenerique config={registreWoTool} />;
}
