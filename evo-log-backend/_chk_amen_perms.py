import re
import pathlib
from app.core.permission_catalog import iter_permission_rows, ROLE_GRANTS

src = pathlib.Path('app/routers/v1/amenagement_extra_deep.py').read_text(encoding='utf-8')
codes = sorted(set(re.findall(r'require_perm\("([^"]+)"\)', src)))
cat = {r[0] for r in iter_permission_rows()}
amen_cat = sorted(r[0] for r in iter_permission_rows() if r[2] == 'amenagement')
print('=== router codes (25) ===')
for c in codes:
    print(('PHANTOM ' if c not in cat else 'ok      ') + c)
print('=== amenagement catalog codes (', len(amen_cat), ') ===')
for c in amen_cat:
    print(c)
