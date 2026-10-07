'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreRoute } from '@/components/courier-express/registres';

export default function PageCourierRoute() {
  return <RegistreGenerique config={registreRoute} />;
}
