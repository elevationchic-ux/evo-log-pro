'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreCashForecast } from '@/components/finance-ohada/registres';

export default function PageCashForecast() {
  return <RegistreGenerique config={registreCashForecast} />;
}
