import re
import pathlib
from app.core.permission_catalog import iter_permission_rows

src = pathlib.Path('app/routers/v1/amenagement_extra_deep.py').read_text(encoding='utf-8')
codes = sorted(set(re.findall(r'require_perm\("([^"]+)"\)', src)))
cat = {r[0] for r in iter_permission_rows()}
print('total codes', len(codes))
print('phantoms:', [c for c in codes if c not in cat])
