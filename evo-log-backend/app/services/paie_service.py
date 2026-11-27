"""Service metier paie : cumuls annuels par salarie (brut, retenues
impot, net) et masse salariale mensuelle. Aucune donnee inventee :
seuls les salaires payes comptent."""
from decimal import Decimal
from typing import Dict, Any

from sqlalchemy.orm import Session

from app.models.rh import Salaire


class PaieService:
    """Cumuls paie."""

    @staticmethod
    def cumuls_annuels(db: Session, annee: int = None) -> Dict[str, Any]:
        q = db.query(Salaire).filter(Salaire.statut != "annule")
        if annee:
            q = q.filter(Salaire.annee == annee)
        salaires = q.all()
        if not salaires:
            return {"annee": annee, "salaires": 0,
                    "note": "Aucun bulletin."}

        par_employe: Dict[int, Dict[str, float]] = {}
        masse_brute = Decimal(0)
        masse_impot = Decimal(0)
        masse_net = Decimal(0)
        for s in salaires:
            eid = s.employe_id
            brut = Decimal(str(s.salaire_brut or 0))
            impot = Decimal(str(s.deductions_impot or 0))
            net = Decimal(str(s.salaire_net or 0))
            par_employe.setdefault(eid, {"brut": 0.0, "impot": 0.0, "net": 0.0, "mois": 0})
            par_employe[eid]["brut"] += float(brut)
            par_employe[eid]["impot"] += float(impot)
            par_employe[eid]["net"] += float(net)
            par_employe[eid]["mois"] += 1
            masse_brute += brut
            masse_impot += impot
            masse_net += net

        return {
            "annee": annee,
            "bulletins_total": len(salaires),
            "employes": len(par_employe),
            "masse_brute_xaf": float(masse_brute),
            "masse_impot_xaf": float(masse_impot),
            "masse_nette_xaf": float(masse_net),
            "par_employe": par_employe,
        }

    @staticmethod
    def cumuls_progressifs(db: Session, annee: int, employe_id: int) -> Dict[str, Any]:
        """Methode du taux cumule : pour chaque mois, l'impot du mois
        = IRGM(cumul base / nb mois) x nb mois - IRGM deja retenu.

        Le barème IRGM (source unique : rh_avance_service) est applique
        sur le salaire imposable mensuel moyen cumule — méthode
        progressive officielle de retenue à la source. L'ecart avec
        deductions_impot persiste est restitue honnetement."""
        from app.services.rh_avance_service import PaieOHADAService

        salaires = db.query(Salaire).filter(
            Salaire.employe_id == employe_id,
            Salaire.annee == annee,
            Salaire.statut != "annule",
        ).order_by(Salaire.mois).all()
        if not salaires:
            return {"employe_id": employe_id, "annee": annee,
                    "mois": [], "note": "Aucun bulletin."}

        cumul_base = Decimal(0)
        cumul_impot_retenu = Decimal(0)
        cumul_impot_du = Decimal(0)
        lignes = []
        for i, s in enumerate(salaires, start=1):
            brut = Decimal(str(s.salaire_brut or 0))
            cnps = Decimal(str(s.deductions_cnps or 0))
            base = brut - cnps
            cumul_base += base
            retenu = Decimal(str(s.deductions_impot or 0))
            cumul_impot_retenu += retenu
            # IRGM du mois = barème sur moyenne mensuelle cumulee x mois - cumule du
            moy = float(cumul_base) / i
            impot_cumule_attendu = PaieOHADAService.calculer_irmg(moy) * i
            impot_mois = max(Decimal(str(impot_cumule_attendu)) - cumul_impot_du, Decimal(0))
            cumul_impot_du += impot_mois
            lignes.append({
                "mois": s.mois,
                "base_imposable": float(base),
                "cumul_base": float(cumul_base),
                "impot_mois_calcule": float(impot_mois),
                "impot_mois_retenu": float(retenu),
                "ecart": float(retenu - impot_mois),
            })

        return {
            "employe_id": employe_id,
            "annee": annee,
            "mois": lignes,
            "impot_annuel_calcule": float(cumul_impot_du),
            "impot_annuel_retenu": float(cumul_impot_retenu),
            "ecart_annuel": float(cumul_impot_retenu - cumul_impot_du),
        }

    @staticmethod
    def bulletin(db: Session, employe_id: int, annee: int, mois: int) -> Dict[str, Any]:
        """Bulletin de paie detaille : brut, primes, retenues CNPS/IRGM,
        net. Refuse honnetement si absent."""
        from app.services.rh_avance_service import PaieOHADAService

        s = db.query(Salaire).filter(
            Salaire.employe_id == employe_id,
            Salaire.annee == annee,
            Salaire.mois == mois,
            Salaire.statut != "annule",
        ).first()
        if not s:
            return {"employe_id": employe_id, "annee": annee, "mois": mois,
                    "note": "Aucun bulletin pour cette periode."}

        brut = float(s.salaire_brut or 0)
        cnps_retraite = brut * PaieOHADAService.TAUX_CNPS_PENSION
        cnps_accident = brut * PaieOHADAService.TAUX_CNPS_ACCIDENTS
        total_cnps = cnps_retraite + cnps_accident
        base = brut - total_cnps
        irgm_calcule = PaieOHADAService.calculer_irmg(base)
        retenu = float(s.deductions_impot or 0)

        return {
            "employe_id": employe_id,
            "annee": annee,
            "mois": mois,
            "salaire_brut": brut,
            "heures_sup": float(s.heures_sup or 0),
            "primes": float(s.primes or 0),
            "cnps_retraite": round(cnps_retraite, 2),
            "cnps_accident": round(cnps_accident, 2),
            "total_cnps": round(total_cnps, 2),
            "base_imposable": round(base, 2),
            "irmg_calcule": round(irgm_calcule, 2),
            "impot_retenu": retenu,
            "ecart_impot": round(retenu - irgm_calcule, 2),
            "autres_deductions": float(s.deductions or 0),
            "salaire_net": float(s.salaire_net or 0),
            "statut": s.statut,
            "devise": "XAF",
        }

    @staticmethod
    def bulletin_pdf(db: Session, employe_id: int, annee: int, mois: int) -> bytes:
        """Genere le PDF du bulletin (WeasyPrint). RuntimeError si
        bibliotheques natives absentes — l'appelant sert alors le HTML."""
        b = PaieService.bulletin(db, employe_id, annee, mois)
        if "note" in b:
            raise RuntimeError(b["note"])
        html = PaieService._bulletin_html(b)
        try:
            from weasyprint import HTML
        except (ImportError, OSError) as exc:
            raise RuntimeError(
                f"Generation PDF indisponible : {exc}.") from exc
        try:
            return HTML(string=html).write_pdf()
        except (ImportError, OSError) as exc:
            raise RuntimeError(
                f"Generation PDF indisponible dans cet environnement ({exc})."
            ) from exc

    @staticmethod
    def _bulletin_html(b: Dict[str, Any]) -> str:
        lignes = "".join(
            f"<tr><td>{k}</td><td style='text-align:right'>{v:,.0f} XAF</td></tr>"
            if isinstance(v, float) else f"<tr><td>{k}</td><td>{v}</td></tr>"
            for k, v in [
                ("Salaire brut", b["salaire_brut"]),
                ("Heures supplementaires", b["heures_sup"]),
                ("Primes", b["primes"]),
                ("CNPS retraite (4,2 %)", b["cnps_retraite"]),
                ("CNPS accidents (0,5 %)", b["cnps_accident"]),
                ("Base imposable", b["base_imposable"]),
                ("IRGM calcule", b["irmg_calcule"]),
                ("Impôt retenu", b["impot_retenu"]),
                ("Autres deductions", b["autres_deductions"]),
                ("Salaire net", b["salaire_net"]),
            ])
        return f"""<!doctype html><html><head><meta charset="utf-8">
<title>Bulletin {b['annee']}-{b['mois']:02d}</title>
<style>body{{font-family:sans-serif;margin:40px}}table{{width:100%;border-collapse:collapse}}
td{{padding:6px;border-bottom:1px solid #ddd}}h1{{font-size:20px}}</style>
</head><body>
<h1>Bulletin de paie — {b['annee']}-{b['mois']:02d}</h1>
<p>Employe #{b['employe_id']} — statut : {b['statut']}</p>
<table>{lignes}</table>
<p><em>Document genere par EVO-LOG — donnees reelles, ecart impôt
{b['ecart_impot']:+.0f} XAF.</em></p>
</body></html>"""
