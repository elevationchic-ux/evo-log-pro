import traceback
try:
    import app.main
    from app.main import app
    routes_m = [r for r in app.routes if hasattr(r, 'path') and '/maintenance-industrielle' in r.path]
    routes_t = [r for r in app.routes if hasattr(r, 'path') and '/tracabilite' in r.path]
    print("maintenance routes mounted:", len(routes_m), "expected 101")
    print("tracabilite routes mounted:", len(routes_t), "expected 77")
    if routes_m:
        print("sample maint:", sorted({r.path for r in routes_m})[:5])
    if routes_t:
        print("sample trace:", sorted({r.path for r in routes_t})[:5])
except Exception:
    traceback.print_exc()
