'use client';

/**
 * Registre des schémas directeurs & périmètres du domaine.
 *
 * La page ne contient aucune donnée et ne formule aucun champ : elle monte le
 * châssis commun avec la configuration déclarée de `registres.ts`, miroir exact
 * des schémas Pydantic du backend. Le vocabulaire (natures, statuts) et les
 * places portuaires restent servis par l'API.
 */
import RegistrePortuaire from '@/components/amenagement-portuaire/RegistrePortuaire';
import { registreSchemas } from '@/components/amenagement-portuaire/registres';

export default function AmenagementPortuaireSchemasDirecteursPage() {
  return <RegistrePortuaire config={registreSchemas} />;
}
