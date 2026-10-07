'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreChfDeliveryAppointment } from '@/components/portail-chauffeur/registres_c';

export default function PageChfDeliveryAppointment() {
  return <RegistreGenerique config={registreChfDeliveryAppointment} />;
}
