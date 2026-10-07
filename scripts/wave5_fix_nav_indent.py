# -*- coding: utf-8 -*-
"""Re-indente les 6 accolades d'ouverture de sous-module mal indentees (8->6 espaces).

Effet de bord de l'insertion splice : la premiere entree inseree dans chaque
tableau subModules se retrouve a 8 espaces alors que ses champs internes sont a
8 (normal). Les autres accolades d'entree sont a 6. On cible uniquement celles
qui precedent les labels connus de la Vague A.
"""
import io

P = r"c:\Users\chris\Documents\Projet\Documents\evo-log pro\evo-log-frontend\src\config\navigationRegistry.ts"
labels = [
    '"Rendez-vous quais (dock scheduling)"',
    '"Sections de voie navigable"',
    '"Lettres de transport house (HAWB)"',
    '"Essieux et roulements"',
    '"Affectation chauffeurs"',
    '"Quasi-accidents (situations dangereuses)"',
]
lines = io.open(P, encoding="utf-8").read().split("\n")
fixed = 0
for i in range(1, len(lines)):
    if lines[i].strip().startswith("label:") and any(l in lines[i] for l in labels):
        if lines[i - 1] == "        {":
            lines[i - 1] = "      {"
            fixed += 1
io.open(P, "w", encoding="utf-8").write("\n".join(lines))
print("re-indented:", fixed)
