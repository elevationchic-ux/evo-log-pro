"""Garde d'encodage : BOM, caractere de remplacement et sur-encodage (mojibake).

Pourquoi ce script existe : sous Windows PowerShell 5, `Set-Content -Encoding
UTF8` ecrit un BOM, et une relecture de fichier UTF-8 en cp1252 produit du texte
sur-encode  un « e » accentue devient deux caracteres (Ã puis ©), un tiret de
separator de section devient trois (â, ” et €). Ce texte EST du UTF-8 valide :
un simple « decode-t-il ? » ne le voit pas, et il se retrouve alors dans les
summary OpenAPI et les messages `detail` servis aux agents, a l'ecran de l'agent
comme dans ses exports.

Detection par aller-retour auto-validant : une ligne n'est declaree suspecte
que si son encoding cp1252 est du UTF-8 valide et donne un texte DIFFERENT.
Un vrai texte francais (« chateau », « enregistre ») echoue au round-trip et
n'est jamais signale. La regle qui detecte est donc exactement la regle qui
repare : un garde a deux logiques est un garde qui ment a moitie.

Usage :
    python scripts/check_encodage.py              # audit, sortie 1 si signalement
    python scripts/check_encodage.py --corriger   # reecrit le reparable, rapporte le reste

Ce qui n'est PAS reparable automatiquement : un caractere de remplacement U+FFFD
signale que l'information etait deja perdue a l'ecriture (un emoji tronque). Il
faut revenir au document source, pas le deviner  le script le laisse donc sur
sa faim et le compte.
"""
import pathlib
import sys

RACINE = pathlib.Path(__file__).resolve().parents[1]
# Le frontend porte aussi des libelles francais : un fichier .tsx sur-encode
# afficherait des accents doubles a l'agent, pas seulement dans une reponse d'API.
FRONT = RACINE.parent / "evo-log-frontend" / "src"
DOSSIERS = ("app", "migrations", "tests", "scripts")
BOM = b"\xef\xbb\xbf"

# Les cinq slots sans affectation de cp1252 (0x81, 0x8D, 0x8F, 0x90, 0x9D) : les
# convertisseurs les rendent souvent par le code point latin-1 identique. Un emoji
# sur-encode peut en contenir (le selecteur de presentation U+FE0F devient trois
# octets dont 0x8F) ; sans ce pont, l'aller-retour echoue et la ligne pourrie
# passerait inapercue alors qu'elle s'affiche en hiéroglyphe chez l'agent.
_TROUS_CP1252 = {0x81: b"\x81", 0x8D: b"\x8d", 0x8F: b"\x8f", 0x90: b"\x90", 0x9D: b"\x9d"}


def _encoder_cp1252(ligne):
    octets = bytearray()
    for caractere in ligne:
        try:
            octets += caractere.encode("cp1252")
        except UnicodeEncodeError:
            trou = _TROUS_CP1252.get(ord(caractere))
            if trou is None:
                raise
            octets += trou
    return bytes(octets)


def reparer_ligne(ligne):
    """Version propre de la ligne, ou None si elle n'est pas sur-encodee."""
    if ligne.isascii() or "\ufffd" in ligne:
        return None
    try:
        candidat = _encoder_cp1252(ligne).decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return None
    return candidat if candidat != ligne else None


def suspects(texte):
    """(ligne, motif, extrait) pour tout ce que le regard de l'agent merite de voir."""
    trouees = []
    for i, ligne in enumerate(texte.split("\n"), start=1):
        if "\ufffd" in ligne:
            trouees.append((i, "caractere de remplacement U+FFFD", ligne.strip()[:70]))
            continue
        if reparer_ligne(ligne):
            trouees.append((i, "texte sur-encode", ligne.strip()[:70]))
    return trouees


def corriger_fichier(chemin, texte):
    """Reecrit ligne par ligne. Ne touche jamais aux lignes deja propres."""
    lignes = texte.split("\n")
    touchees = 0
    for i, ligne in enumerate(lignes):
        propre = reparer_ligne(ligne)
        if propre is not None:
            lignes[i] = propre
            touchees += 1
    if touchees:
        chemin.write_bytes("\n".join(lignes).encode("utf-8"))
    return touchees


def main():
    # La console Windows est en cp1252 : un extrait signalé contient justement le
    # texte pourri que l'on traque (emoji, accents doubles). Sans réencodage, le
    # garde meurt d'un UnicodeEncodeError au milieu de son rapport.
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    mode_corriger = "--corriger" in sys.argv
    problems = 0
    racines = [(RACINE / d, (".py",)) for d in DOSSIERS]
    if FRONT.exists():
        racines.append((FRONT, (".ts", ".tsx")))
    for base, extensions in racines:
        for p in sorted(x for x in base.rglob("*") if x.suffix in extensions and x.is_file()):
            raw = p.read_bytes()
            rel = p.relative_to(RACINE.parent)
            if raw.startswith(BOM):
                if mode_corriger:
                    p.write_bytes(raw[len(BOM):])
                    print(f"{rel}: BOM UTF-8 retire")
                    continue
                print(f"{rel}: BOM UTF-8 (corriger l'outil qui a ecrit le fichier)")
                problems += 1
                continue
            try:
                texte = raw.decode("utf-8")
            except UnicodeDecodeError as exc:
                print(f"{rel}: n'est pas du UTF-8 strict ({exc})")
                problems += 1
                continue
            if mode_corriger:
                nb = corriger_fichier(p, texte)
                if nb:
                    print(f"{rel}: {nb} ligne(s) reencodee(s)")
                texte = p.read_text(encoding="utf-8")
            for ligne, motif, extrait in suspects(texte):
                print(f"{rel}:{ligne}: {motif}  {extrait!r}")
                problems += 1
    if problems:
        print(f"\n{problems} signalement(s). Reencoder proprement avant de pousser.")
        return 1
    print("Encodage OK (aucun BOM, aucun U+FFFD, aucun sur-encodage).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
