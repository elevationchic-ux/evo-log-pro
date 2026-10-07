import traceback
try:
    import app.models  # noqa
    from app.models import tracabilite_deep  # noqa - ensure imported
    from app.models.maintenance_deep import Base
    from app.core.database import engine
    print("Base is same:", Base is tracabilite_deep.Base)
    tabs = [t for t in Base.metadata.tables.values() if t.name.startswith(("maint_", "trace_"))]
    maint = sorted(t.name for t in tabs if t.name.startswith("maint_"))
    trace = sorted(t.name for t in tabs if t.name.startswith("trace_"))
    print(f"maint={len(maint)}  trace={len(trace)}")
    missing = []
    for t in tabs:
        for col in t.columns:
            for fk in col.foreign_keys:
                target = fk.target_fullname.split(".")[0]
                if target not in Base.metadata.tables:
                    missing.append((t.name, col.name, target))
    if missing:
        print("MISSING FK TARGETS:", missing)
    else:
        Base.metadata.create_all(bind=engine, tables=tabs, checkfirst=True)
        print("create_all wave6 OK")
except Exception:
    traceback.print_exc()
