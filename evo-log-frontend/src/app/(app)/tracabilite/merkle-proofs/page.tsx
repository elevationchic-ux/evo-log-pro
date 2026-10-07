'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreMerkleProof } from '@/components/tracabilite/registres';

export default function PageIntegrityMerkleProof() {
  return <RegistreGenerique config={registreMerkleProof} />;
}
