"""Garde d'encodage : BOM, caractere de remplacement et sur-encodage (mojibake).

Pourquoi ce script existe : sous Windows PowerShell 5, `Set-Content -Encoding
UTF8` ecrit un BOM, et une relecture de fichier UTF-8 en cp1252 produit du
texte sur-encode (« DÃ©clarer », « â”€ »). Ce texte EST du UTF-8 valide : un
simple « decode-t-il ? » ne le voit pas, et il se retrouve alors dans les
summary OpenAPI et les messages `detail` servis aux agents.

Detection par aller-retour auto-validant : une ligne n'est declaree suspecte
que si son encoding cp1252 est du UTF-8 VALIDIE et donne un texte DIFFERENT.
Un vrai texte francais (« chateau », « enregistre ») echoue au round-trip et
n'est jamais signale. Le script ne reecrit rien : il dit ou est le probleme.

Usage : python scripts/check_encodage.py   (sortie 1 si au moins un fichier)
"""
import pathlib
import sys

RACINE = pathlib.Path(__file__).resolve().parents[1]
DOSSIERS = ("app", "migrations", "tests", "scripts")
BOM = b"\xef\xbb\xbf"


def suspects(texte):
    """Lignes dont le round-trip cp1252 -> utf-8 produit un texte different."""
    trouees = []
    for i, ligne in enumerate(texte.split("\n"), start=1):
        if "\ufffd" in ligne:
            trouees.append((i, "caractere de remplacement U+FFFD", ligne.strip()[:70]))
            continue
        if ligne.isascii():
            continue
        try:
            candidat = ligne.encode("cp1252").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            continue
        if candidat != ligne:
            trouees.append((i, "texte sur-encode", ligne.strip()[:70]))
    return trouees


def main():
    problems = 0
    for dossier in DOSSIERS:
        for p in sorted((RACINE / dossier).rglob("*.py")):
            raw = p.read_bytes()
            rel = p.relative_to(RACINE)
            if raw.startswith(BOM):
                print(f"{rel}: BOM UTF-8 (corriger l'outil qui a ecrit le fichier)")
                problems += 1
                continue
            try:
                texte = raw.decode("utf-8")
            except UnicodeDecodeError as exc:
                print(f"{rel}: n'est pas du UTF-8 strict ({exc})")
                problems += 1
                continue
            for ligne, motif, extrait in suspects(texte):
                print(f"{rel}:{ligne}: {motif} — {extrait!r}")
                problems += 1
    if problems:
        print(f"\n{problems} signalement(s). Reencoder proprement avant de pousser.")
        return 1
    print("Encodage OK (aucun BOM, aucun U+FFFD, aucun sur-encodage).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
