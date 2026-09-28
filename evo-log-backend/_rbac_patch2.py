"""Upgrade transport routers from get_current_user to require_perm RBAC."""
import re
import pathlib

ROUTER_DIR = pathlib.Path("app/routers/v1")
FILES = [
    "transport_avance.py",
    "transport_avance_complete.py",
    "transport_exploitation.py",
    "transport_international.py",
]

# Permission mapping by router file
PERM_MAP = {
    "transport_avance.py": {
        "GET": "transport.dispatch.read",
        "POST": "transport.dispatch.create",
        "PUT": "transport.dispatch.modify",
        "PATCH": "transport.dispatch.modify",
        "DELETE": "transport.dispatch.modify",
    },
    "transport_avance_complete.py": {
        "GET": "transport.mission.read",
        "POST": "transport.mission.create",
        "PUT": "transport.mission.modify",
        "PATCH": "transport.mission.modify",
        "DELETE": "transport.mission.delete",
    },
    "transport_exploitation.py": {
        "GET": "transport.mission.read",
        "POST": "transport.mission.create",
        "PUT": "transport.mission.modify",
        "PATCH": "transport.mission.modify",
        "DELETE": "transport.mission.delete",
    },
    "transport_international.py": {
        "GET": "transport.mission.read",
        "POST": "transport.mission.create",
        "PUT": "transport.mission.modify",
        "PATCH": "transport.mission.modify",
        "DELETE": "transport.mission.delete",
    },
}

for filename in FILES:
    fp = ROUTER_DIR / filename
    content = fp.read_text(encoding="utf-8")
    
    # Add require_perm import if not already present
    if "from app.core.permissions import require_perm" not in content:
        # Insert after the first import from app.core
        content = content.replace(
            "from app.core.security import get_current_user",
            "from app.core.permissions import require_perm\nfrom app.core.security import get_current_user",
            1,
        )
    
    perms = PERM_MAP[filename]
    
    # Find each @router.METHOD(...) decorator and the function signature below
    # Replace Depends(get_current_user) with Depends(require_perm("..."))
    # based on the HTTP method
    
    # Pattern: @router.get/post/put/patch/delete(...) ... async def ...(... current_user: User = Depends(get_current_user) ...)
    pattern = r'@router\.(get|post|put|patch|delete)\('
    
    lines = content.split('\n')
    new_lines = []
    current_method = None
    replaced = 0
    
    for line in lines:
        m = re.search(pattern, line)
        if m:
            current_method = m.group(1).upper()
        
        # Replace Depends(get_current_user) with Depends(require_perm(...))
        if current_method and "Depends(get_current_user)" in line and "current_user" in line:
            perm_code = perms.get(current_method, "transport.mission.read")
            line = line.replace(
                "Depends(get_current_user)",
                f'Depends(require_perm("{perm_code}"))',
            )
            replaced += 1
        
        new_lines.append(line)
    
    content = '\n'.join(new_lines)
    fp.write_text(content, encoding="utf-8")
    print(f"{filename}: {replaced} endpoints upgraded to require_perm")

print("Done.")
