"""Import du tarif CEMAC OFFICIEL dans la nomenclature (positions SH -> taux).

PRINCIPE D'HONNETETE : ce script ne INVENTE AUCUN taux. Il ne fait que charger
des donnees provenant d'un fichier officiel fourni par l'operateur (arrete
tarifaire CEMAC / export DGD-CAMCIS). Sans fichier, sans source declaree ou
sans ligne valide, il echoue bruyamment et n'ecrit rien.

Le moteur UNIQUE de liquidation (app/services/taxation_douaniere.py) resout le
droit de douane depuis cette table ; une fois le tarif reel importe, les
simulations "defaut 20%" disparaissent au profit de taux reels traces.

Format d'entree (CSV ou JSON, une entree par position SH) :
    Colonnes obligatoires : code_hs, description, taux_dd, taux_tva
    Colonnes optionnelles  : section, chapitre, position, unite, statut,
                             date_effet (AAAA-MM-JJ), date_fin_effet,
                             source_reference

    - code_hs   : 6 a 8 chiffres (position SH).
    - taux_dd / taux_tva : pourcentages numeriques entre 0 et 100
                  (ex. 20 pour 20 %, 19.25 pour 19,25 %).
    - toute ligne manquante/un taux absent est REJETEE (jamais completee par
      une valeur par defaut silencieuse).

Usage :
    python scripts/import_tarif_cemac.py --file tarif_cemac_2026.csv \
        --source "Arrete CEMAC n.XXX-2026 (DGD)" [--dry-run]
    python scripts/import_tarif_cemac.py --print-template
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REQUIRED_COLUMNS = ("code_hs", "description", "taux_dd", "taux_tva")
CSV_HEADER = ",".join(
    ("code_hs", "description", "taux_dd", "taux_tva", "section", "chapitre",
     "position", "unite", "statut", "date_effet", "date_fin_effet",
     "source_reference")
)
_CODE_HS = re.compile(r"^\d{6,8}$")


def _parse_date(value: Any, champ: str, ligne: int) -> Tuple[date | None, str | None]:
    if value in (None, ""):
        return None, None
    if isinstance(value, (date, datetime)):
        return (value.date() if isinstance(value, datetime) else value), None
    texte = str(value).strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(texte, fmt).date(), None
        except ValueError:
            continue
    return None, f"ligne {ligne}: {champ}='{texte}' n'est pas une date AAAA-MM-JJ"


def _parse_taux(value: Any, champ: str, ligne: int) -> Tuple[float | None, str | None]:
    if value in (None, ""):
        return None, f"ligne {ligne}: {champ} manquant (aucun taux par defaut invente)"
    try:
        taux = float(str(value).replace(",", ".").strip())
    except (TypeError, ValueError):
        return None, f"ligne {ligne}: {champ}='{value}' n'est pas numerique"
    if not (0.0 <= taux <= 100.0):
        return None, f"ligne {ligne}: {champ}={taux} hors [0..100]"
    return taux, None


def charger_lignes(chemin: Path) -> List[Dict[str, Any]]:
    texte = chemin.read_text(encoding="utf-8-sig")
    if chemin.suffix.lower() == ".json":
        data = json.loads(texte)
        if not isinstance(data, list):
            raise ValueError("Le JSON doit etre une liste d'objects.")
        return data
    # Sinon CSV ( ou TSV ) : sniff de delimiteur.
    delim = "\t" if chemin.suffix.lower() in (".tsv",) else ","
    return list(csv.DictReader(texte.splitlines(), delimiter=delim))


def valider_et_normaliser(lignes: List[Dict[str, Any]]) -> Tuple[List[dict], List[str]]:
    valide: List[dict] = []
    erreurs: List[str] = []

    for i, row in enumerate(lignes, start=2 if lignes and "code_hs" in (lignes[0] or {}) else 1):
        code = str((row or {}).get("code_hs", "")).strip()
        if not _CODE_HS.match(code):
            erreurs.append(f"ligne {i}: code_hs='{code}' doit contenir 6 a 8 chiffres")
            continue

        description = str((row or {}).get("description", "")).strip()
        if not description:
            erreurs.append(f"ligne {i} ({code}): description manquante")
            continue

        taux_dd, err = _parse_taux((row or {}).get("taux_dd"), "taux_dd", i)
        if err:
            erreurs.append(err)
            continue
        taux_tva, err = _parse_taux((row or {}).get("taux_tva"), "taux_tva", i)
        if err:
            erreurs.append(err)
            continue

        d_effet, err = _parse_date((row or {}).get("date_effet"), "date_effet", i)
        if err:
            erreurs.append(err)
            continue
        d_fin, err = _parse_date((row or {}).get("date_fin_effet"), "date_fin_effet", i)
        if err:
            erreurs.append(err)
            continue

        # chapitre/position derivables de facon DETERMINISTE depuis le SH
        # (2 et 4 premiers chiffres) ; section (romaine) non -> seulement si fournie.
        valide.append({
            "code_hs": code,
            "description": description,
            "taux_dd": taux_dd,
            "taux_tva": taux_tva,
            "section": (str(row.get("section", "")).strip() or None),
            "chapitre": (str(row.get("chapitre", "")).strip() or code[:2]),
            "position": (str(row.get("position", "")).strip() or code[:4]),
            "unite": (str(row.get("unite", "")).strip() or None),
            "statut": (str(row.get("statut", "")).strip() or "actif"),
            "date_effet": d_effet,
            "date_fin_effet": d_fin,
            "source_reference": (str(row.get("source_reference", "")).strip() or None),
        })
    return valide, erreurs


def importer(db, entries: List[dict], source_globale: str, lot: str, dry_run: bool) -> Tuple[int, int]:
    from app.models.transit_avance import NomenclatureCEMAC

    inserted = updated = 0
    today = date.today()
    for e in entries:
        source = e["source_reference"] or f"{source_globale} [{lot}]"
        existant = db.query(NomenclatureCEMAC).filter(
            NomenclatureCEMAC.code_hs == e["code_hs"]
        ).first()
        if existant is None:
            db.add(NomenclatureCEMAC(
                code_hs=e["code_hs"], description=e["description"],
                section=e["section"], chapitre=e["chapitre"], position=e["position"],
                taux_dd=e["taux_dd"], taux_tva=e["taux_tva"], unite=e["unite"],
                statut=e["statut"], date_effet=e["date_effet"] or today,
                date_fin_effet=e["date_fin_effet"], source_reference=source,
            ))
            inserted += 1
        else:
            for champ in ("description", "section", "chapitre", "position",
                          "unite", "statut", "date_fin_effet"):
                if e[champ] is not None:
                    setattr(existant, champ, e[champ])
            existant.taux_dd = e["taux_dd"]
            existant.taux_tva = e["taux_tva"]
            existant.date_effet = e["date_effet"] or existant.date_effet or today
            existant.source_reference = source
            updated += 1

    if dry_run:
        db.rollback()
    else:
        db.commit()
    return inserted, updated


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Import du tarif CEMAC officiel (aucun taux invente).")
    parser.add_argument("--file", help="Chemin du CSV/TSV/JSON officiel.")
    parser.add_argument("--source", help="Reference de la source officielle (ex. arrete, fichier DGD).")
    parser.add_argument("--dry-run", action="store_true", help="Valide sans ecrire en base.")
    parser.add_argument("--print-template", action="store_true", help="Affiche l'en-tete attendue puis quitte.")
    args = parser.parse_args(argv)

    if args.print_template:
        print("# En-tete attendue (remplir avec les taux OFFICIELS, ne jamais laisser un taux vide) :")
        print(CSV_HEADER)
        return 0

    if not args.file:
        print("ERREUR : --file est requis (voir --print-template pour le format).", file=sys.stderr)
        return 2
    chemin = Path(args.file)
    if not chemin.exists():
        print(f"ERREUR : fichier introuvable : {chemin}", file=sys.stderr)
        return 2
    if not args.dry_run and not args.source:
        print("ERREUR : --source (reference officielle) est requis pour ecrire en base.", file=sys.stderr)
        return 2

    try:
        lignes = charger_lignes(chemin)
    except (ValueError, json.JSONDecodeError) as exc:
        print(f"ERREUR : lecture du fichier impossible : {exc}", file=sys.stderr)
        return 2

    if not lignes:
        print("ERREUR : fichier vide, aucune ligne a importer.", file=sys.stderr)
        return 2

    entries, erreurs = valider_et_normaliser(lignes)
    for err in erreurs:
        print(f"  REJET : {err}", file=sys.stderr)

    if not entries:
        print(f"ECHEC : 0 ligne valide sur {len(lignes)} (voir rejets ci-dessus). "
              f"Aucune donnee inventee, rien n'est ecrit.", file=sys.stderr)
        return 1

    from app.core.database import SessionLocal
    db = SessionLocal()
    try:
        lot = f"import:{chemin.name}"
        ins, up = importer(db, entries, args.source or "saisie import", lot, args.dry_run)
        mode = "DRY-RUN (rien ecrit)" if args.dry_run else "ECRIT"
        print(f"[{mode}] {ins} insertion(s), {up} mise(s) a jour, "
              f"{len(erreurs)} rejet(s) sur {len(lignes)} ligne(s).")
    finally:
        db.close()
    return 0 if not erreurs else 0


if __name__ == "__main__":
    raise SystemExit(main())
