'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreSparePart } from '@/components/maintenance-industrielle/registres';

export default function PageSparePartCatalog() {
  return <RegistreGenerique config={registreSparePart} />;
}
