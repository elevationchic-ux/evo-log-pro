"""Apply RBAC to transport.py endpoints that lack auth."""
import pathlib

fp = pathlib.Path("app/routers/v1/transport.py")
content = fp.read_text(encoding="utf-8")

pairs = [
    ("async def create_chauffeur(conducteur_data: ConducteurCreate, db: Session = Depends(get_db)):",
     'async def create_chauffeur(conducteur_data: ConducteurCreate, db: Session = Depends(get_db), current_user: User = Depends(require_perm("transport.mission.create"))):'),
    ("async def create_conducteur(conducteur_data: ConducteurCreate, db: Session = Depends(get_db)):",
     'async def create_conducteur(conducteur_data: ConducteurCreate, db: Session = Depends(get_db), current_user: User = Depends(require_perm("transport.mission.create"))):'),
    ("async def get_all_missions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):",
     'async def get_all_missions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(require_perm("transport.mission.read"))):'),
    ("async def get_mission(mission_id: int, db: Session = Depends(get_db)):",
     'async def get_mission(mission_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_perm("transport.mission.read"))):'),
    ("async def update_mission_status(mission_id: int, mission_data: MissionUpdate, db: Session = Depends(get_db)):",
     'async def update_mission_status(mission_id: int, mission_data: MissionUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_perm("transport.mission.modify"))):'),
    ("async def create_mission(mission_data: MissionCreate, db: Session = Depends(get_db)):",
     'async def create_mission(mission_data: MissionCreate, db: Session = Depends(get_db), current_user: User = Depends(require_perm("transport.mission.create"))):'),
    ("async def update_mission(mission_id: int, mission_data: MissionUpdate, db: Session = Depends(get_db)):",
     'async def update_mission(mission_id: int, mission_data: MissionUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_perm("transport.mission.modify"))):'),
    ("async def list_missions_root(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):",
     'async def list_missions_root(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(require_perm("transport.mission.read"))):'),
    ("async def optimiser_tournees_vrp(payload: dict = None):",
     'async def optimiser_tournees_vrp(payload: dict = None, current_user: User = Depends(require_perm("transport.dispatch.read"))):'),
    ("async def obtenir_statut_corridors_cemac(db: Session = Depends(get_db)):",
     'async def obtenir_statut_corridors_cemac(db: Session = Depends(get_db), current_user: User = Depends(require_perm("transport.dispatch.read"))):'),
    ("async def obtenir_tco_flotte(db: Session = Depends(get_db)):",
     'async def obtenir_tco_flotte(db: Session = Depends(get_db), current_user: User = Depends(require_perm("parc.flotte.read"))):'),
    ("async def get_transport_kpis(db: Session = Depends(get_db)):",
     'async def get_transport_kpis(db: Session = Depends(get_db), current_user: User = Depends(require_perm("transport.mission.read"))):'),
]

applied = 0
missing = 0
for old, new in pairs:
    if old in content:
        content = content.replace(old, new)
        applied += 1
    else:
        print(f"NOT FOUND: {old[:70]}...")
        missing += 1

fp.write_text(content, encoding="utf-8")
print(f"Done: {applied} applied, {missing} not found")
