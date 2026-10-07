"""Cree les 12 page.tsx pour port-operations (Wave 1A frontend)."""
import os
from pathlib import Path

PAGES = [
    ("draft-surveys", "DraftSurvey"),
    ("stevedoring-crews", "StevedoringCrew"),
    ("cargo-handling-plans", "CargoHandlingPlan"),
    ("quay-equipment", "QuayEquipment"),
    ("pilotage-towage/pilotage", "PilotageSession"),
    ("pilotage-towage/towage", "TowageOperation"),
    ("bunkering", "BunkeringOrder"),
    ("vessel-waste", "VesselWasteReceipt"),
    ("tally-inspection", "TallySheet"),
    ("demurrage-storage", "DemurrageCase"),
    ("gate-passes", "GatePass"),
    ("container-yard", "YardOperation"),
]

# Simplification : pilotage et remorquage partagent un slug. Utiliser des slugs distincts.
PAGES = [
    ("draft-surveys", "DraftSurvey"),
    ("stevedoring-crews", "StevedoringCrew"),
    ("cargo-handling-plans", "CargoHandlingPlan"),
    ("quay-equipment", "QuayEquipment"),
    ("pilotage-sessions", "PilotageSession"),
    ("towage-operations", "TowageOperation"),
    ("bunkering", "BunkeringOrder"),
    ("vessel-waste", "VesselWasteReceipt"),
    ("tally-inspection", "TallySheet"),
    ("demurrage-storage", "DemurrageCase"),
    ("gate-passes", "GatePass"),
    ("container-yard", "YardOperation"),
]

ROOT = Path(__file__).resolve().parents[1] / "evo-log-frontend" / "src" / "app" / "(app)" / "port-operations"

TEMPLATE = """'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import {{ registre{cn} }} from '@/components/port-operations/registres';

export default function Page{cn}() {{
  return <RegistreGenerique config={{registre{cn}}} />;
}}
"""

for slug, cn in PAGES:
    target = ROOT / slug
    target.mkdir(parents=True, exist_ok=True)
    (target / "page.tsx").write_text(TEMPLATE.format(cn=cn), encoding="utf-8")
    print(f"WROTE {target / 'page.tsx'}")
