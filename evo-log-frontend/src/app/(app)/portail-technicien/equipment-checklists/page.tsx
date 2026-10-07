'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreTechEquipmentChecklist } from '@/components/portail-technicien/registres_c';

export default function PageTechEquipmentChecklist() {
  return <RegistreGenerique config={registreTechEquipmentChecklist} />;
}
