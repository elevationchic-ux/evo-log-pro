'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreInfrastructureMaintenance } from '@/components/amenagement-portuaire/registres_portuaires';

export default function PageInfrastructureMaintenance() {
  return <RegistreGenerique config={registreInfrastructureMaintenance} />;
}
