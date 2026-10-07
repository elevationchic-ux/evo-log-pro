'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreDomainArchive } from '@/components/amenagement-portuaire/registres_expansion';

export default function PageDomainArchive() {
  return <RegistreGenerique config={registreDomainArchive} />;
}
