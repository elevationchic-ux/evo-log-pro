'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreExceptionEx } from '@/components/courier-express/registres';

export default function PageCourierException() {
  return <RegistreGenerique config={registreExceptionEx} />;
}
