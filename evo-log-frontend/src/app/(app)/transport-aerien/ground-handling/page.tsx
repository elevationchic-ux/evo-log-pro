'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreGroundHandlingJob } from '@/components/transport-aerien/registres';

export default function PageGroundHandlingJob() {
  return <RegistreGenerique config={registreGroundHandlingJob} />;
}
