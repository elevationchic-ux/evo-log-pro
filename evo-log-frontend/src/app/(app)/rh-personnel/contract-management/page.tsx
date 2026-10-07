'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreEmploymentContract } from '@/components/rh-personnel/registres';

export default function PageEmploymentContract() {
  return <RegistreGenerique config={registreEmploymentContract} />;
}
