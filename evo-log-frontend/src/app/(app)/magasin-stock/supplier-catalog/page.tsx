'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreSupplierArticle } from '@/components/magasin-stock/registres';

export default function PageSupplierArticle() {
  return <RegistreGenerique config={registreSupplierArticle} />;
}
