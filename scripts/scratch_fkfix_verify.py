"""Verifie la structure reelle des blocs fixes par fix_fk_order_005_007.py."""
import io
import os

BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "evo-log-backend", "migrations", "versions")
FILES = ["005_add_acconage_transit_avance.py", "007_add_cameroun_cemac.py"]

report = []
for fname in FILES:
    path = os.path.join(BASE, fname)
    src = io.open(path, encoding="utf-8").read()
    lines = src.split("\n")
    report.append(f"===== {fname} ({len(lines)} lignes) =====")
    # compile() explicite
    try:
        compile(src, path, "exec")
        report.append("compile() OK")
    except SyntaxError as exc:
        report.append(f"compile() SYNTAX ERROR: {exc}")
    # localiser MARKER
    marker = "# [fix_fk_order]"
    for i, ln in enumerate(lines):
        if marker in ln:
            report.append("contexte autour ligne %d:" % (i + 1))
            for j in range(max(0, i - 4), min(len(lines), i + 6)):
                report.append("  %5d|%r" % (j + 1, lines[j]))
            report.append("")
    # ou est la fin du corps de upgrade() ?
    ui = src.index("def upgrade(")
    di = src.find("def downgrade(")
    report.append(f"upgrade() commence offset {ui}, downgrade() offset {di}")
    # prochaine def apres upgrade
    import re
    for m in re.finditer(r"^def \w+", src[ui:], re.M):
        report.append(f"  def apres upgrade: offset {ui + m.start()} -> {src[ui + m.start():ui + m.start() + 40]!r}")
    report.append("")

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_fkfix_verify.txt")
io.open(out, "w", encoding="utf-8").write("\n".join(report))
print("wrote", out)
