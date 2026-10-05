"""Une seule ligne a corriger : le glyphe casse est irremplacable par aller-retour.

Le caractere de remplacement U+FFFD signale une information deja perdue a
l'ecriture (emoji tronque). On ne le devine pas : on le remplace par le signe
que le fichier donne deja a la douane ('transit-douane': '🛃'), et on le dit en
commentaire pour que le geste reste relisable.
"""
import pathlib

CHEMIN = pathlib.Path(__file__).resolve().parents[2] / "evo-log-frontend" / "src" / "config" / "moduleColors.ts"
REPLACED = "\ufffd"
ICONE_DOUE = "🛃"  # signe deja employe pour la douane dans ce fichier

texte = CHEMIN.read_text(encoding="utf-8")
lignes = texte.split("\n")
visees = [i for i, l in enumerate(lignes) if REPLACED in l]
assert visees == [82], visees
ancienne = lignes[82]
assert ancienne.count(REPLACED) == 1, ancienne
nouvelle = ancienne.replace("'" + REPLACED + "'", "'" + ICONE_DOUE + "'")
explication = "\n".join([
    "  // 'magasin-douane' portait un caractere de remplacement (emoji tronque a",
    "  // l'ecriture). Un glyphe casse n'est pas une icone, et comme la chaine est",
    "  // non vide le repli '|| 📋' ne jouait pas : on remet le signe deja employe",
    "  // pour la douane dans ce fichier ('transit-douane').",
])
lignes[82] = explication + "\n" + nouvelle
CHEMIN.write_text("\n".join(lignes), encoding="utf-8", newline="")
print("avant:", repr(ancienne))
print("apres:", repr(nouvelle))
