'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreArticleCatalog } from '@/components/magasin-stock/registres';

export default function PageArticleCatalog() {
  return <RegistreGenerique config={registreArticleCatalog} />;
}
