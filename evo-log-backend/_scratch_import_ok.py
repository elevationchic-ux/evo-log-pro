import traceback
try:
    # Force full models package import to register all tables
    import app.models  # noqa
    from app.models.maintenance_deep import Base
    from app.core.database import engine
    tabs_m = [t for n, t in Base.metadata.tables.items() if n.startswith("maint_")]
    tabs_t = [t for n, t in Base.metadata.tables.items() if n.startswith("trace_")]
    print("maint tables:", len(tabs_m), sorted(n for n, t in Base.metadata.tables.items() if n.startswith("maint_")))
    print("trace tables:", len(tabs_t), sorted(n for n, t in Base.metadata.tables.items() if n.startswith("trace_")))
    # verify all FK targets exist
    missing = []
    for t in tabs_m + tabs_t:
        for fk in [c for col in t.columns for c in col.foreign_keys]:
            if fk._table_key not in Base.metadata.tables:
                missing.append((t.name, col.name, fk._table_key))
    # Simpler: try create_all with just wave 6 tables
    Base.metadata.create_all(bind=engine, tables=tabs_m + tabs_t, checkfirst=True)
    print("create_all wave6 OK")
except Exception:
    traceback.print_exc()
