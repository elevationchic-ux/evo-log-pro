"""Renomme mecaniquement le sous-module « DTO » en « programmation ».

Motif : « DTO / Document Technique Outil » n'existe pas dans le circuit
camerounais reel. Les pieces reelles sont la fiche / le dossier technique, le
visa de maturite (decret n° 2018/0492), l'inscription au PIP-CDMT et le visa du
controle financier (MINFI). Le renommage porte sur l'ORM, les schemas, le
routeur, le catalogue RBAC et la migration generee.

Remplacements ordonnes (les tokens longs d'abord, sinon le motif court
recapturerait le resultat).
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TARGETS = [
    ROOT / "evo-log-backend" / "app" / "models" / "amenagement_portuaire.py",
    ROOT / "evo-log-backend" / "app" / "schemas" / "amenagement_portuaire.py",
    ROOT / "evo-log-backend" / "app" / "routers" / "v1" / "amenagement_portuaire.py",
    ROOT / "scripts" / "scratch_amgt_gen_migration.py",
]

PAIRS = [
    ("RegistreDTOCreate", "DocumentProgrammationCreate"),
    ("RegistreDTOUpdate", "DocumentProgrammationUpdate"),
    ("RegistreDTOOut", "DocumentProgrammationOut"),
    ("RegistreDTO", "DocumentProgrammation"),
    ("registres_dto_amgt", "documents_programmation_amgt"),
    ("reference_dto", "reference_fiche_technique"),
    ("date_notification_minepf", "date_notification_minfi"),
    ("amenagement.dto.", "amenagement.programmation."),
    ('"/dto', '"/programmation'),
    ("/dto/", "/programmation/"),
    ("lister_dto", "lister_programmation"),
    ("creer_dto", "creer_programmation"),
    ("detail_dto", "detail_programmation"),
    ("modifier_dto", "modifier_programmation"),
    ("viser_dto", "viser_programmation"),
    ("notifier_minepf", "notifier_minfi"),
    ("MINEPF", "MINFI"),
    ("T_DTO", "T_PROGRAMMATION"),
    ('"DTO"', '"PROGRAMMATION"'),
]

for path in TARGETS:
    if not path.exists():
        print("absent, ignore :", path.name)
        continue
    src = original = path.read_text(encoding="utf-8")
    for old, new in PAIRS:
        src = src.replace(old, new)
    if src == original:
        print("inchange :", path.name)
        continue
    path.write_text(src, encoding="utf-8")
    print("reecrit :", path.name, len(original), "->", len(src))
