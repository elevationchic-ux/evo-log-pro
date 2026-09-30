import io, glob, re

# L'echelle z de (app)/layout.tsx reserve z-100 aux modales applicatives :
# z-50 se retrouvait sous le backdrop mobile (55) et le drawer (60).
changed_files = 0
raised = 0
for f in glob.glob("src/**/*.tsx", recursive=True):
    lines = io.open(f, encoding="utf-8").read().split("\n")
    hit = 0
    for i, line in enumerate(lines):
        if "fixed inset-0" in line and re.search(r"\bz-50\b", line):
            lines[i] = re.sub(r"\bz-50\b", "z-[100]", line)
            hit += 1
    if hit:
        io.open(f, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
        changed_files += 1
        raised += hit
print("files patched:", changed_files, "overlays raised:", raised)

left = []
for f in glob.glob("src/**/*.tsx", recursive=True):
    s = io.open(f, encoding="utf-8").read()
    for m in re.finditer(r"[^\n]*\bz-50\b[^\n]*", s):
        left.append((f, m.group(0).strip()[:110]))
print("remaining z-50 (non modal overlay):", len(left))
seen = set()
for f, l in left:
    if l in seen:
        continue
    seen.add(l)
    print("  ", f, "|", l)
