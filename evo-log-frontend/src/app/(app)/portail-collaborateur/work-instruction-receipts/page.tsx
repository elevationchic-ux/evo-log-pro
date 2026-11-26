'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreCollWorkInstructionReceipt } from '@/components/portail-collaborateur/registres_c';

export default function PageCollWorkInstructionReceipt() {
  return <RegistreGenerique config={registreCollWorkInstructionReceipt} />;
}
