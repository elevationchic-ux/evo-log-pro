'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreRecentDocument } from '@/components/dashboard/registres';

export default function PageRecentDocument() {
  return <RegistreGenerique config={registreRecentDocument} />;
}
