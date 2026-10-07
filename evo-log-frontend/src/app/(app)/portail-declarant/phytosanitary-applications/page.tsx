'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreDeclPhytosanitaryApp } from '@/components/portail-declarant/registres_c';

export default function PageDeclPhytosanitaryApp() {
  return <RegistreGenerique config={registreDeclPhytosanitaryApp} />;
}
