import traceback
try:
    from app.models import maintenance_deep, tracabilite_deep
    from app.core.database import engine
    from app.models.maintenance_deep import Base as MD_Base
    from app.models.tracabilite_deep import Base as TD_Base
    # both share Base
    tabs_m = [t for t in MD_Base.metadata.sorted_tables if t.name.startswith("maint_")]
    tabs_t = [t for t in TD_Base.metadata.sorted_tables if t.name.startswith("trace_")]
    print("maint tables count:", len(tabs_m), [t.name for t in tabs_m])
    print("trace tables count:", len(tabs_t), [t.name for t in tabs_t])
    MD_Base.metadata.create_all(bind=engine, tables=tabs_m + tabs_t, checkfirst=True)
    print("create_all OK all wave 6")
except Exception:
    traceback.print_exc()
