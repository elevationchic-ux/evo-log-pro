'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreCustody } from '@/components/tracabilite/registres';

export default function PageChainOfCustodyTransfer() {
  return <RegistreGenerique config={registreCustody} />;
}
