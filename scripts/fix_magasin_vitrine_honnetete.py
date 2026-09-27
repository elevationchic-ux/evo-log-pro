"""
Remplace les 9 pages vitrine "Système K-Magasin Connecté" par un message honnete
"Fonctionnalite non deployee" — supprime le mensonge (ShieldCheck vert + "connecte")
sans casser la navigation ni les titres specifiques a chaque ecran.

Pattern a remplacer (commun aux 9 fichiers):
    <ShieldCheck ... />
    <div>
        <h4 ...>Système K-Magasin Connecté</h4>
        <p ...>Toutes les données ... temps réel ...</p>
    </div>

Remplacement:
    <AlertTriangle ... />  (warn color)
    <div>
        <h4 ...>Fonctionnalité non déployée</h4>
        <p ...>...</p>
    </div>

Le script modifie uniquement la section "badge" et laisse le reste (titre, sous-titre,
lien Retour). Idempotent: ne touche pas les pages deja corrigees.
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent / "evo-log-frontend/src/app/(app)/magasin"

BADGE_PATTERN = re.compile(
    r"""(<div\s+className="p-8\s+bg-slate-950[^"]*"[^>]*>)\s*"""
    r"""<ShieldCheck\s+className="w-8\s+h-8\s+text-emerald-400[^"]*"\s*/>\s*"""
    r"""<div>\s*"""
    r"""<h4\s+className="[^"]*"[^>]*>.*?(?:Connect[eé]|connect[eé]).*?</h4>\s*"""
    r"""<p\s+className="[^"]*"[^>]*>.*?</p>\s*"""
    r"""</div>\s*""",
    re.DOTALL | re.IGNORECASE,
)

NEW_BADGE = (
    '<div className="p-8 bg-slate-950 border border-slate-800 rounded-2xl flex items-center gap-4">'
    ' <AlertTriangle className="w-8 h-8 text-amber-400 shrink-0" />'
    ' <div>'
    '  <h4 className="font-bold text-amber-200">Fonctionnalit\u00e9 non d\u00e9ploy\u00e9e</h4>'
    '  <p className="text-xs text-slate-400 mt-0.5">'
    '   Cet \u00e9cran affiche un espace r\u00e9serv\u00e9 : la logique backend liee \u00e0 cette '
    'vue n\u2019est pas encore c\u00e2bl\u00e9e. Revenez apr\u00e8s d\u00e9ploiement ou consultez '
    '<a href="/magasin/dashboard" className="text-sky-400 underline">le tableau de bord magasin</a>.'
    '  </p>'
    ' </div>'
)


def fix_file(path: pathlib.Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if "Fonctionnalit" in text and "non d" in text and "ploy" in text:
        return False  # already fixed
    new_text, n = BADGE_PATTERN.subn(NEW_BADGE, text, count=1)
    if n == 0:
        return False
    # Ensure AlertTriangle is imported
    if "AlertTriangle" not in new_text.split("export default")[0]:
        new_text = re.sub(
            r"from 'lucide-react';",
            "from 'lucide-react';\nimport { AlertTriangle } from 'lucide-react';",
            new_text,
            count=1,
        )
        # Remove duplicate import if ShieldCheck was the only lucide import
        new_text = new_text.replace(
            "import { AlertTriangle } from 'lucide-react';\nimport { Warehouse, ArrowLeft, ShieldCheck } from 'lucide-react';",
            "import { Warehouse, ArrowLeft, AlertTriangle } from 'lucide-react';",
            1,
        )
    path.write_text(new_text, encoding="utf-8", newline="\n")
    return True


if __name__ == "__main__":
    fixed = 0
    skipped = 0
    for p in sorted(ROOT.rglob("page.tsx")):
        if fix_file(p):
            fixed += 1
            print(f"FIXED   {p.relative_to(ROOT.parent.parent)}")
        else:
            content = p.read_text(encoding="utf-8")
            if "Systeme" in content or "Syst" in content and "Connect" in content:
                print(f"CHECK   {p.relative_to(ROOT.parent.parent)} (pattern not matched)")
            skipped += 1
    print(f"\n{fixed} pages corrected, {skipped - fixed} unchanged.")
