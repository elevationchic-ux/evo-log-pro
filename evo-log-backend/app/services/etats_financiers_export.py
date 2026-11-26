"""Export PDF des etats financiers SYSCOHADA (bilan, CR, TAFIRE, TFT, SIG,
liasse fiscale) via WeasyPrint.

Le document est genere depuis les etats PERSISTES du grand livre — jamais
d'inventer des chiffres : si un etat n'existe pas pour l'exercice, sa
section est explicitement marquee « non genere », pas simulee."""
from typing import Optional

from sqlalchemy.orm import Session

from app.models.finance_ohada import (
    BilanOHADADetaille, CompteResultatOHADADetaille, TAFIRE, TFT, SIG,
    LiasseFiscale, ExerciceComptable, AnnexesOHADA,)


def _fmt(val) -> str:
    if val is None:
        return "—"
    try:
        return f"{float(val):,.2f}".replace(",", " ").replace(".", ",")
    except (TypeError, ValueError):
        return "—"


def _ligne(label: str, val, fort: bool = False) -> str:
    style = "font-weight:700" if fort else ""
    return f'<tr><td style="padding:3px 8px;border-bottom:1px solid #eee">{label}</td><td style="text-align:right;padding:3px 8px;border-bottom:1px solid #eee;{style}">{_fmt(val)}</td></tr>'


def _section(titre: str, lignes: list, note: Optional[str] = None) -> str:
    if not lignes:
        return f'<h3>{titre}</h3><p style="color:#888;font-style:italic">Non genere</p>'
    rows = "".join(lignes)
    extra = f'<p style="font-size:11px;color:#666">{note}</p>' if note else ""
    return f"<h3>{titre}</h3><table style='width:100%;border-collapse:collapse'>{rows}</table>{extra}"


def generer_html_exercice(db: Session, exercice_id: int) -> str:
    """Construit le HTML des etats financiers (base du PDF et du fallback)."""
    exercice = db.query(ExerciceComptable).filter(ExerciceComptable.id == exercice_id).first()
    if not exercice:
        raise ValueError("Exercice comptable introuvable")

    def _dernier(model):
        return (
            db.query(model)
            .filter(model.exercice_id == exercice_id)
            .order_by(model.id.desc())
            .first()
        )

    bilan = _dernier(BilanOHADADetaille)
    cr = _dernier(CompteResultatOHADADetaille)
    tafire = _dernier(TAFIRE)
    tft = _dernier(TFT)
    sig = _dernier(SIG)
    annexes = _dernier(AnnexesOHADA)
    liasse = db.query(LiasseFiscale).filter(
        LiasseFiscale.annee == exercice.annee).order_by(LiasseFiscale.id.desc()).first()

    sections = []

    sections.append(_section("Bilan (SYSCOHADA)", [
        _ligne("Actif immobilise net", bilan.actif_immobilise_net if bilan else None, True),
        _ligne("Stocks", bilan.actif_circulant_stocks if bilan else None),
        _ligne("Creances", bilan.actif_circulant_creances if bilan else None),
        _ligne("Tresorerie-actif", bilan.tresorerie_actif if bilan else None),
        _ligne("TOTAL ACTIF", bilan.total_actif if bilan else None, True),
        _ligne("Capitaux propres", bilan.capitaux_propres_total if bilan else None),
        _ligne("Dettes", bilan.dettes_courtes if bilan else None),
        _ligne("TOTAL PASSIF", bilan.total_passif if bilan else None, True),
    ], "Actif = Passif garanti par la partie double." if bilan else None))

    sections.append(_section("Compte de resultat", [
        _ligne("Produits d'exploitation", cr.total_produits_exploitation if cr else None),
        _ligne("Charges d'exploitation", cr.total_charges_exploitation if cr else None),
        _ligne("Resultat d'exploitation", cr.resultat_exploitation if cr else None, True),
        _ligne("Resultat net", cr.resultat_net if cr else None, True),
    ]))

    sections.append(_section("TAFIRE", [
        _ligne("Capacite d'autofinancement", tafire.capacit_autofinancement if tafire else None),
        _ligne("Total ressources", tafire.total_ressources if tafire else None),
        _ligne("Total emplois", tafire.total_emplois if tafire else None),
        _ligne("Variation de tresorerie", tafire.variation_tresorerie if tafire else None, True),
        _ligne("Tresorerie de fin", tafire.tresorerie_fin if tafire else None, True),
    ]))

    sections.append(_section("TFT (flux de tresorerie)", [
        _ligne("Flux d'exploitation", tft.flux_exploitation if tft else None),
        _ligne("Flux d'investissement", tft.flux_investissement if tft else None),
        _ligne("Flux de financement", tft.flux_financement if tft else None),
        _ligne("Variation de tresorerie", tft.variation_tresorerie if tft else None, True),
        _ligne("Tresorerie de fin", tft.tresorerie_fin if tft else None, True),
    ]))

    sections.append(_section("SIG", [
        _ligne("Effectif moyen", sig.effectif_moyen if sig else None),
        _ligne("Masse salariale", sig.masse_salariale if sig else None),
        _ligne("Chiffre d'affaires", sig.chiffre_affaires if sig else None),
        _ligne("EBE", sig.excédent_brut_exploitation if sig else None),
        _ligne("CAF", sig.capacite_autofinancement if sig else None),
        _ligne("Investissements", sig.investissements if sig else None),
        _ligne("BFR", sig.besoin_en_fonds_de_roulement if sig else None),
        _ligne("Tresorerie nette", sig.tresorerie_nette if sig else None),
        _ligne("Resultat net", sig.resultat_net if sig else None, True),
    ]))

    if liasse:
        sections.append(_section(f"Liasse fiscale CEMAC {liasse.annee}", [
            _ligne("Declarations TVA", liasse.nombre_declarations_tva),
            _ligne("TVA collectee", liasse.total_tva_collectee),
            _ligne("TVA deductible", liasse.total_tva_deductible),
            _ligne("TVA a payer", liasse.total_tva_a_payer),
            _ligne("IS", liasse.total_is),
            _ligne("TOTAL IMPOTS", liasse.total_impots, True),
        ], f"Statut : {liasse.statut}"))

    if annexes:
        sections.append(f"<h3>Annexes</h3><p>{annexes.denomination_sociale or ''} — "
                        f"{annexes.forme_juridique or ''} — {annexes.siege_social or ''}</p>")

    return f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>
body {{ font-family: 'DejaVu Sans', sans-serif; font-size: 11px; color:#1a1a1a; margin:40px; }}
h1 {{ font-size:16px; color:#0d2b52; border-bottom:2px solid #c9a227; padding-bottom:6px; }}
h3 {{ font-size:12px; color:#0d2b52; margin-top:18px; }}
.meta {{ color:#666; font-size:10px; margin-bottom:12px; }}
footer {{ margin-top:30px; font-size:9px; color:#999; border-top:1px solid #eee; padding-top:6px; }}
</style></head><body>
<h1>Etats financiers SYSCOHADA — Exercice {exercice.annee}</h1>
<p class="meta">Exercice {exercice.numero_exercice} du {exercice.date_debut} au {exercice.date_fin}
 — Document genere depuis le grand livre, {exercice.statut}</p>
{''.join(sections)}
<footer>Document interne — ne vaut pas certification par un commissaire aux comptes.</footer>
</body></html>"""


def generer_pdf_exercice(db: Session, exercice_id: int) -> bytes:
    """Genere le PDF des etats financiers de l'exercice (WeasyPrint).

    Leève RuntimeError si WeasyPrint ou ses bibliothèques natives
    (Pango/Cairo) sont absentes — l'appelant doit alors servir le HTML."""
    html = generer_html_exercice(db, exercice_id)
    try:
        from weasyprint import HTML
    except (ImportError, OSError) as exc:
        raise RuntimeError(
            "Generation PDF indisponible : WeasyPrint ou ses bibliotheques "
            f"natives manquent dans cet environnement ({exc})."
        ) from exc
    try:
        return HTML(string=html).write_pdf()
    except (ImportError, OSError) as exc:
        raise RuntimeError(
            f"Generation PDF indisponible dans cet environnement ({exc})."
        ) from exc
