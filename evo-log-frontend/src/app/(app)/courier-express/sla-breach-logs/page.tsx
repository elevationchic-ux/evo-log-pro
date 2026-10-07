'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreCour2SlaBreachLog } from '@/components/courier-express/registres_e';

export default function PageCour2SlaBreachLog() {
  return <RegistreGenerique config={registreCour2SlaBreachLog} />;
}
