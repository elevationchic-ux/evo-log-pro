'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreCommSalesOrder } from '@/components/portail-commercial/registres_c';

export default function PageCommSalesOrder() {
  return <RegistreGenerique config={registreCommSalesOrder} />;
}
