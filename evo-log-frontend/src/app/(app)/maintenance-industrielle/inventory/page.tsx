'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreInventory } from '@/components/maintenance-industrielle/registres';

export default function PagePartInventory() {
  return <RegistreGenerique config={registreInventory} />;
}
