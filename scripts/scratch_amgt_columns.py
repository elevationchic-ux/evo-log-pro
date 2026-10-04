"""Longueurs VARCHAR reellement generees par l'ORM pour les colonnes enum du
modele amenagement_portuaire (la migration 038 doit les reproduire a l'identique).
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "evo-log-backend"))

import app.models.port_cameroun  # noqa: F401  (referentiel FK)
import app.models.amenagement_portuaire as m  # noqa: E402
from sqlalchemy.orm import configure_mappers  # noqa: E402

configure_mappers()

classes = [
    m.SchemaDirecteur, m.ProjetAmenagement, m.RegistreDTO, m.MarcheAmenagement,
    m.AutorisationDomaniale, m.ConcessionPortuaire, m.InfrastructurePortuaire,
    m.Dragage, m.AutorisationTravaux,
]
for cls in classes:
    t = cls.__table__
    print("--", t.name)
    for col in t.columns:
        typ = col.type
        rendered = typ.compile() if not hasattr(typ, "length") else f"{typ.__class__.__name__}({typ.length})"
        print(f"   {col.name:34s} {str(rendered):28s} null={col.nullable} "
              f"default={col.default.arg if col.default is not None and hasattr(col.default, 'arg') else None} "
              f"index={col.index} unique={col.unique} fk={[str(fk.target_fullname) for fk in col.foreign_keys]}")
