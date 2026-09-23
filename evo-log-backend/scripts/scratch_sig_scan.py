import inspect

import app.services.integration_service as isvc
import app.services.magasin_douane_service as msvc

print("### integration_service classes")
for name, obj in vars(isvc).items():
    if inspect.isclass(obj) and any(m.startswith("creer") or m.startswith("traiter") or m.startswith("activer") for m, _ in inspect.getmembers(obj, predicate=inspect.isfunction)):
        print("==", name)
        for m, f in inspect.getmembers(obj, predicate=inspect.isfunction):
            if not m.startswith("_"):
                print("   ", m, inspect.signature(f))

print("### magasin_douane_service classes")
for name, obj in vars(msvc).items():
    if inspect.isclass(obj) and name.endswith("Service"):
        print("==", name)
        for m, f in inspect.getmembers(obj, predicate=inspect.isfunction):
            if not m.startswith("_"):
                print("   ", m, inspect.signature(f))

print("### models statut/enums")
from app.models.integration import Integration, RequeteIntegration, SYDONIAPlus, GuichetUnique, PCS, TypeIntegration, TypeRequete
print("TypeIntegration", [m.value for m in TypeIntegration])
print("TypeRequete", [m.value for m in TypeRequete])
for M in (Integration, RequeteIntegration, SYDONIAPlus, GuichetUnique, PCS):
    print(M.__name__, "cols:", [c.name for c in M.__table__.columns])

from app.models.magasin_douane import EntrepotDouane, DeclarationEntrepot, FicheMagasin, SurveillanceEntrepot
for M in (EntrepotDouane, DeclarationEntrepot, FicheMagasin, SurveillanceEntrepot):
    print(M.__name__, "cols:", [(c.name, c.default.arg if c.default and c.default.is_scalar else None) for c in M.__table__.columns])
