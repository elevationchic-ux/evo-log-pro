'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreCmptcJournalReversal } from '@/components/comptabilite-ohada/registres_c';

export default function PageCmptcJournalReversal() {
  return <RegistreGenerique config={registreCmptcJournalReversal} />;
}
