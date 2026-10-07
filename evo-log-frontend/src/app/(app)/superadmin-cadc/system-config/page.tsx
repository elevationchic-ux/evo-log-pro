'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreGlobalConfigSetting } from '@/components/superadmin-cadc/registres';

export default function PageGlobalConfigSetting() {
  return <RegistreGenerique config={registreGlobalConfigSetting} />;
}
