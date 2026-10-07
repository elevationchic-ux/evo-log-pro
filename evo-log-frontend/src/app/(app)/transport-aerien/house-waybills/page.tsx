'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreHouseAirWaybill } from '@/components/transport-aerien/registres_b';

export default function PageHouseAirWaybill() {
  return <RegistreGenerique config={registreHouseAirWaybill} />;
}
