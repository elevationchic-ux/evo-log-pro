"""Add require_perm to transport_exploitation.py which has NO auth at all."""
import re
import pathlib

fp = pathlib.Path("app/routers/v1/transport_exploitation.py")
content = fp.read_text(encoding="utf-8")

# Add import if not present
if "from app.core.permissions import require_perm" not in content:
    # Insert after "from app.core.database import get_db"
    content = content.replace(
        "from app.core.database import get_db",
        "from app.core.database import get_db\nfrom app.core.permissions import require_perm\nfrom app.models.user import User",
        1,
    )

# Pattern: @router.METHOD(...) followed by async def name(params):\n
# We need to insert current_user param before the closing ):
# Match the last parameter line before the ):

# Find all route decorators and their function signatures
pattern = r'(@router\.(get|post|put|patch|delete)\([^)]*\)\s*\n(?:\s*@[^\n]+\n)*async def \w+\([^)]*)\n'

def add_perm(match):
    sig_block = match.group(1)
    method = match.group(2).upper()
    
    # Determine permission
    if method == "GET":
        perm = "transport.mission.read"
    elif method == "POST":
        perm = "transport.mission.create"
    elif method in ("PUT", "PATCH"):
        perm = "transport.mission.modify"
    elif method == "DELETE":
        perm = "transport.mission.delete"
    else:
        perm = "transport.mission.read"
    
    # Only add if not already present
    if "current_user" not in sig_block:
        # Insert before the final ) or )\n
        # Find the last param and add after it
        sig_block = sig_block.rstrip()
        if sig_block.endswith(":"):
            # Remove the colon, add param, re-add colon
            sig_block = sig_block[:-1].rstrip()
            if sig_block.endswith(","):
                sig_block += f' current_user: User = Depends(require_perm("{perm}")):'
            else:
                sig_block += f', current_user: User = Depends(require_perm("{perm}")):'
        elif sig_block.endswith(")"):
            # The closing ) of the params
            sig_block = sig_block[:-1]
            if sig_block.endswith(","):
                sig_block += f' current_user: User = Depends(require_perm("{perm}"))):'
            else:
                sig_block += f', current_user: User = Depends(require_perm("{perm}"))):'
    
    return sig_block + "\n"

# Use a different approach: line-by-line with state tracking
lines = content.split('\n')
new_lines = []
i = 0
upgraded = 0

while i < len(lines):
    line = lines[i]
    m = re.match(r'@router\.(get|post|put|patch|delete)\(', line.strip())
    if m:
        method = m.group(1).upper()
        if method == "GET":
            perm = "transport.mission.read"
        elif method == "POST":
            perm = "transport.mission.create"
        elif method in ("PUT", "PATCH"):
            perm = "transport.mission.modify"
        elif method == "DELETE":
            perm = "transport.mission.delete"
        else:
            perm = "transport.mission.read"
        
        # Collect lines until we find the function signature end (line ending with :)
        func_lines = []
        found_def = False
        j = i
        while j < len(lines):
            func_lines.append(lines[j])
            if re.match(r'async def \w+\(', lines[j].strip()) or re.match(r'def \w+\(', lines[j].strip()):
                found_def = True
            if found_def and lines[j].rstrip().endswith(':'):
                break
            j += 1
        
        # Check if current_user already exists in the collected lines
        func_block = '\n'.join(func_lines)
        if "current_user" not in func_block and "require_perm" not in func_block:
            # Insert before the last line (the one ending with : or ):)
            last = func_lines[-1].rstrip()
            # The last line is like:   db: Session = Depends(get_db),
            # or:   db: Session = Depends(get_db)):
            # or just: ):
            indent = len(last) - len(last.lstrip())
            
            # Find the closing ):  or ) : 
            if last.endswith('):'):
                # Insert new param before )
                insert_line = last[:-2] + f',\n{" " * (indent + 4)}current_user: User = Depends(require_perm("{perm}"))):'
                func_lines[-1] = insert_line
                upgraded += 1
            elif last.endswith(','):
                # Last param line ending with comma, next line should be ):
                # Insert after this line
                func_lines.insert(len(func_lines), f'{" " * (indent)}current_user: User = Depends(require_perm("{perm}")),')
                # Also fix: the closing ) is on next iteration (but we already collected to :)
                # Actually the pattern already includes the ) line
                upgraded += 1
            elif last.endswith(':'):
                # Direct colon after params
                func_lines[-1] = last[:-1] + f' current_user: User = Depends(require_perm("{perm}"))):'
                upgraded += 1
        
        new_lines.extend(func_lines)
        i = j + 1
    else:
        new_lines.append(line)
        i += 1

content = '\n'.join(new_lines)
fp.write_text(content, encoding="utf-8")
print(f"transport_exploitation.py: {upgraded} endpoints upgraded")
