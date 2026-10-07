import traceback
try:
    import app.schemas.maintenance_deep as sm
    import app.schemas.tracabilite_deep as st
    from app.routers.v1 import maintenance_deep as rm, tracabilite_deep as rt
    print("schemas maintenance classes:", sum(1 for n in dir(sm) if n.endswith(("Create","Update","Out"))))
    print("schemas tracabilite classes:", sum(1 for n in dir(st) if n.endswith(("Create","Update","Out"))))
    routes_m = list(rm.router.routes)
    routes_t = list(rt.router.routes)
    print("routes maintenance:", len(routes_m), "expected:", 25*4+1)
    print("routes tracabilite:", len(routes_t), "expected:", 19*4+1)
    # Print first 3 route paths
    for r in routes_m[:3]:
        print("M:", r.path, sorted(r.methods))
    for r in routes_t[:3]:
        print("T:", r.path, sorted(r.methods))
except Exception:
    traceback.print_exc()
