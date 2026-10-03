import sys; sys.path.insert(0,".")
from fastapi.testclient import TestClient
from app.main import app
from app.core.auth import get_current_user

class FakeUser:
    id = 1
    email = "smoke@test.local"
    full_name = "Smoke Test"
    company_id = 1
    is_active = True

app.dependency_overrides[get_current_user] = lambda: FakeUser()
c = TestClient(app)

r = c.post("/api/v1/real-customs/cautions", json={"reference": "SMOKE-CAU-001", "banque_cautionnaire": "Banque Test", "plafond_autorise_xaf": 25000000, "devise": "XAF"})
print("POST caution:", r.status_code, r.json())

r = c.post("/api/v1/real-customs/camcis/circuits", json={"numero_dum": "SMOKE-DUM-001", "circuit": "JAUNE", "inspecteur_assigne": "Insp. Test", "description": "smoke"})
print("POST circuit:", r.status_code, r.json())

r = c.post("/api/v1/real-customs/camcis/teletransmettre", json={"numero_dum": "SMOKE-DUM-001", "numero_accuse_camcis": "ACC-SMOKE-1"})
print("POST teletrans:", r.status_code, r.json())

r = c.get("/api/v1/real-customs/camcis/circuits/SMOKE-DUM-001")
print("GET circuit:", r.status_code, r.json())

r = c.get("/api/v1/real-customs/cautions/statut")
d = r.json()
print("GET statut:", r.status_code, {k: d[k] for k in ("nb_cautions_actives","plafond_autorise_xaf","montant_engage_xaf","disponible_xaf","taux_utilisation_pourcent","alerte_depassement")})

r = c.post("/api/v1/real-customs/cautions/apurer", json={"numero_dum": "SMOKE-DUM-001", "numero_quittance": "QUIT-SMOKE-1"})
print("POST apurer:", r.status_code, r.json())

r = c.get("/api/v1/real-customs/camcis/circuits/SMOKE-DUM-001")
d = r.json()
print("verif apure:", d.get("apure"), d.get("numero_quittance"))
