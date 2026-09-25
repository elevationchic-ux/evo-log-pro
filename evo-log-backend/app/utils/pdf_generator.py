"""Génération PDF : Jinja2 -> HTML -> WeasyPrint.

WeasyPrint a besoin des bibliothèques système Pango/Cairo (installées dans
l'image Docker de production). Si elles sont indisponibles (poste de dev
Windows sans ces DLL, dépendance non installée), le service lève un HTTP 501
explicite  on ne renvoie JAMAIS un faux PDF ni un HTML déguisé en PDF.

Convention alignée sur app/core/not_implemented.py : l'échec est honnête et
dit de quoi l'utilisateur a besoin.
"""
from pathlib import Path
from typing import Any, Dict

from fastapi import HTTPException

TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates" / "pdf"

_env = None


def _get_env():
    """Environment Jinja2, créé à la demande (import paresseux : le module
    doit rester importable même si jinja2 manque, pour un 501 honnête)."""
    global _env
    if _env is None:
        try:
            from jinja2 import Environment, FileSystemLoader
        except ImportError as e:
            raise HTTPException(
                status_code=501,
                detail=f"Génération PDF indisponible : jinja2 n'est pas installé ({e}).",
            )
        _env = Environment(
            loader=FileSystemLoader(str(TEMPLATE_DIR)),
            autoescape=True,
            trim_blocks=True,
            lstrip_blocks=True,
        )
    return _env


def generer_pdf(nom_template: str, contexte: Dict[str, Any]) -> bytes:
    """Rend le template Jinja2 puis le convertit en PDF via WeasyPrint.

    Lève HTTPException(501) si WeasyPrint ou ses librairies natives ne sont
    pas disponibles dans l'environnement courant.
    """
    if not (TEMPLATE_DIR / nom_template).exists():
        raise HTTPException(
            status_code=501,
            detail=f"Modèle PDF '{nom_template}' introuvable côté serveur.",
        )
    html = _get_env().get_template(nom_template).render(**contexte)

    try:
        from weasyprint import HTML
    except (ImportError, OSError) as e:
        raise HTTPException(
            status_code=501,
            detail=(
                "Génération PDF indisponible dans cet environnement : WeasyPrint "
                "ou ses bibliothèques natives (Pango/Cairo) manquent. "
                f"Détail : {e}"
            ),
        )
    try:
        return HTML(string=html).write_pdf()
    except OSError as e:
        raise HTTPException(
            status_code=501,
            detail=f"Échec de rendu PDF (bibliothèques natives indisponibles) : {e}",
        )


# ─── Montant en lettres (français) ───────────────────────────────────────────
# Mention « arrêtée la présente facture à la somme de ... » (usage OHADA/DGI).

_UNITES = (
    "zéro", "un", "deux", "trois", "quatre", "cinq", "six", "sept", "huit",
    "neuf", "dix", "onze", "douze", "treize", "quatorze", "quinze", "seize",
    "dix-sept", "dix-huit", "dix-neuf",
)
_DIZAINES = {
    2: "vingt", 3: "trente", 4: "quarante", 5: "cinquante", 6: "soixante",
    8: "quatre-vingt", 9: "soixante-dix",
}


def _cent_a_quatre_vingt_cents(n: int) -> str:
    if n < 20:
        return _UNITES[n]
    d, u = divmod(n, 10)
    if d in (7, 9):
        # 70-79 -> soixante-dix..., 90-99 -> quatre-vingt-dix...
        base = "soixante" if d == 7 else "quatre-vingt"
        if d == 7 and u == 1:
            return "soixante et onze"
        return f"{base}-{_cent_a_quatre_vingt_cents(10 + u)}"
    dizaines = _DIZAINES[d]
    if u == 0:
        return dizaines + ("s" if d == 8 else "")  # quatre-vingts
    if u == 1 and d != 8:
        return f"{dizaines}-et-un"  # vingt-et-un ... soixante-et-onze
    return f"{dizaines}-{_UNITES[u]}"


def _trois_chiffres(n: int) -> str:
    if n == 0:
        return _UNITES[0]
    c, reste = divmod(n, 100)
    mots = []
    if c:
        if c == 1:
            mots.append("cent")
        else:
            mots.append(f"{_UNITES[c]} cent" + ("s" if reste == 0 else ""))
    if reste:
        mots.append(_cent_a_quatre_vingt_cents(reste))
    return " ".join(mots)


def nombre_en_lettres(n: int) -> str:
    """Entier 0..999 999 999 en toutes lettres (français, orthographe 1990)."""
    if n < 0:
        return f"moins {nombre_en_lettres(-n)}"
    if n < 1000:
        return _trois_chiffres(n)
    millions, reste = divmod(n, 1_000_000)
    milliers, fin = divmod(reste, 1000)
    parts = []
    if millions:
        parts.append(("un" if millions == 1 else _trois_chiffres(millions)) + " million" + ("s" if millions > 1 else ""))
    if milliers:
        # "mille" se dit sans "un" : 1000 = mille, 21000 = vingt et un mille
        parts.append(("" if milliers == 1 else _trois_chiffres(milliers) + " ") + "mille")
    if fin:
        parts.append(_trois_chiffres(fin))
    return " ".join(parts)


def montant_en_lettres(montant: float, devise: str = "XAF") -> str:
    """ex: 1 234 567.89 -> 'deux cent ... francs CFA et quatre-vingt-neuf centimes'."""
    try:
        valeur = float(montant)
    except (TypeError, ValueError):
        return ""
    entier = int(valeur)
    centimes = int(round((valeur - entier) * 100))
    nom_devise = {"XAF": "francs CFA", "XOF": "francs CFA", "EUR": "euros", "USD": "dollars"}.get(devise, devise)
    texte = f"{nombre_en_lettres(entier)} {nom_devise}"
    if centimes:
        texte += f" et {nombre_en_lettres(centimes)} centime" + ("s" if centimes > 1 else "")
    return texte
