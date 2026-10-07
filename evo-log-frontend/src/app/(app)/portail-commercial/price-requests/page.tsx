'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreCommPriceRequest } from '@/components/portail-commercial/registres_c';

export default function PageCommPriceRequest() {
  return <RegistreGenerique config={registreCommPriceRequest} />;
}
