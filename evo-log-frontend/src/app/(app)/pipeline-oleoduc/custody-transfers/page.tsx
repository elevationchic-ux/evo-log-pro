'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registrePipe2CustodyTransfer } from '@/components/pipeline-oleoduc/registres_e';

export default function PagePipe2CustodyTransfer() {
  return <RegistreGenerique config={registrePipe2CustodyTransfer} />;
}
