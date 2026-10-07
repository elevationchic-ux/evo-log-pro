'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreIntercompanyEntry } from '@/components/comptabilite-ohada/registres';

export default function PageIntercompanyEntry() {
  return <RegistreGenerique config={registreIntercompanyEntry} />;
}
