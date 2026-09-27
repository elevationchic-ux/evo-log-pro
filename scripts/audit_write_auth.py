"""Audit: find DELETE/PUT routes that don't enforce granular permissions."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "evo-log-backend"))

from app.main import app
import inspect

no_perm = []
for route in app.routes:
    if not hasattr(route, 'endpoint') or not hasattr(route, 'path'):
        continue
    if not route.path.startswith('/api/'):
        continue
    methods = getattr(route, 'methods', set())
    if 'DELETE' in methods or 'PUT' in methods:
        ep = route.endpoint
        src = ''
        try:
            src = inspect.getsource(ep)
        except Exception:
            pass
        has_perm = 'require_perm' in src or 'role_level' in src or 'is_superuser' in src
        # Also accept get_current_user as "authenticated" (less strict)
        has_auth = 'current_user' in src or 'get_current_user' in src
        if not has_perm and not has_auth:
            verb = 'DELETE' if 'DELETE' in methods else 'PUT'
            no_perm.append(f'{verb:6s} {route.path}')

print(f'WRITE routes (DELETE/PUT) without ANY auth or permission: {len(no_perm)}')
for r in sorted(no_perm)[:20]:
    print(f'  {r}')
