'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreCold2ShipmentApproval } from '@/components/chaine-froid/registres_e';

export default function PageCold2ShipmentApproval() {
  return <RegistreGenerique config={registreCold2ShipmentApproval} />;
}
