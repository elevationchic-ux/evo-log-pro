'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreULDInventory } from '@/components/transport-aerien/registres';

export default function PageULDInventory() {
  return <RegistreGenerique config={registreULDInventory} />;
}
