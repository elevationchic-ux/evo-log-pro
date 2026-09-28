"""
RH router - Complete HR management & Employee Self-Service (Portail Collaborateur) endpoints
Accessible to any employee (non-RH included: Chauffeurs, Magasiniers, Déclarants, Dispatchers, IT, etc.)
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc, extract
from typing import List, Optional, Dict, Any
from datetime import date, datetime, timedelta
from pathlib import Path
import calendar
import mimetypes
import secrets
from html import escape

from app.core.database import get_db
from app.core.config import settings
from app.core.security import get_current_user, get_password_hash, validate_password_strength
from app.utils.rbac import require_role
from app.models.user import User, Role
from app.models.rh import (
    Conge, TypeConge, StatutConge, Absence, TempsTravail,
    Formation, ParticipationFormation, EvaluationPerformance,
    ContratTravail, Salaire, Prime, DocumentEmploye
)
from app.schemas.rh import (
    CongeCreate, CongeUpdate, CongeResponse, SoldeCongeResponse,
    AbsenceCreate, AbsenceUpdate, AbsenceResponse,
    TempsTravailCreate, TempsTravailUpdate, TempsTravailResponse, HeuresMensuellesResponse,
    FormationCreate, FormationUpdate, FormationResponse,
    ParticipationFormationCreate, ParticipationFormationUpdate, ParticipationFormationResponse,
    EvaluationPerformanceCreate, EvaluationPerformanceUpdate, EvaluationPerformanceResponse,
    ContratTravailCreate, ContratTravailUpdate, ContratTravailResponse,
    SalaireCreate, SalaireResponse,
    PrimeCreate, PrimeResponse,
    DocumentEmployeCreate, DocumentEmployeUpdate, DocumentEmployeResponse,
    OrganigrammeCreate, OrganigrammeUpdate, OrganigrammeResponse,
    CompetenceCreate, CompetenceUpdate, CompetenceResponse,
    CompetenceEmployeCreate, CompetenceEmployeUpdate, CompetenceEmployeResponse
)
from app.services.rh_service import (
    CongeService, AbsenceService, TempsTravailService, FormationService,
    PerformanceService, ContratService, PaieService, DocumentEmployeService,
    OrganigrammeService, CompetenceService
)
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field

router = APIRouter(tags=["RH"])
security_scheme = HTTPBearer(auto_error=True)

# Ecritures RH (paie, creation d'un salarie, decisions sur les conges) :
# casquette RH/DRH, admin entreprise (niveau 1) ou Super Admin. La lecture du
# portail personnel reste ouverte a tout salarie.
requireRH = require_role(["RH", "DRH", "ADMIN", "1"])


def resolve_rh_user(current_user: User = Depends(get_current_user)) -> User:
    """Use the central database-backed authentication dependency."""
    return current_user


def get_user_role_label(user: User) -> str:
    """Helper to get user's corporate job title."""
    if user.is_superuser:
        return "Direction Générale & Superviseur Système"
    if user.roles:
        r = user.roles[0]
        if r.description:
            return r.description.split(" - ")[0]
        return r.name
    return "Collaborateur Opérationnel"


# ============================================================================
# 👤 PORTAIL EMPLOYÉ RH (ACCESSIBLE À TOUT SALARIÉ NON-RH)
# ============================================================================

class PortailDemandeCongeIn(BaseModel):
    type_conge: str
    date_debut: date
    date_fin: date
    motif: Optional[str] = ""


@router.get("/portail/me")
def get_portail_mon_profil(
    db: Session = Depends(get_db),
    current_user: User = Depends(resolve_rh_user)
):
    """Profil RH du salarie connecte, en donnees reellement enregistrees uniquement.

    Ce qui n'a jamais ete saisi par la DRH remonte a ``null`` (matricule, numero
    CNPS, compte bancaire, date d'embauche) et l'ecran affiche « Non renseigne ».
    Inventer un numero de securite sociale ou un RIB sur un portail social n'est
    pas un remplissage : c'est un faux document.

    Le droit a conges de 24 jours ouvrables par annee revolue est une regle de
    valeur du Code du travail camerounais, pas une donnee locale.
    """
    droit_conge_annuel = 24
    annee_courante = date.today().year

    contrat = db.query(ContratTravail).filter(
        ContratTravail.employe_id == current_user.id
    ).order_by(ContratTravail.date_debut.desc()).first()

    conges_pris = db.query(Conge).filter(
        Conge.employe_id == current_user.id,
        Conge.statut == StatutConge.APPROUVE,
        extract('year', Conge.date_debut) == annee_courante,
    ).all()
    jours_utilises = sum(int(c.nombre_jours or 0) for c in conges_pris)
    solde_restant = max(0, droit_conge_annuel - jours_utilises)

    # Dernier bulletin reellement paye : rien n'est evalue en l'absence de paie
    last_salaire = db.query(Salaire).filter(
        Salaire.employe_id == current_user.id
    ).order_by(Salaire.periode_fin.desc()).first()

    return {
        "id": current_user.id,
        "full_name": current_user.full_name or current_user.username,
        "username": current_user.username,
        "email": current_user.email,
        "phone": current_user.phone,
        "matricule": current_user.matricule,
        "poste": current_user.job_title or (contrat.poste if contrat else None),
        "departement": current_user.department.nom if current_user.department else None,
        "agence": current_user.agency.name if current_user.agency else None,
        "statut_contrat": contrat.type_contrat if contrat else None,
        "date_embauche": contrat.date_debut.isoformat() if contrat and contrat.date_debut else None,
        # Aucun champ dedie n'existe pour ces informations : elles remontent
        # null plutot qu'un numero CNPS ou un RIB calcule arbitrairement.
        "cnps_matricule": None,
        "couverture_sociale": None,
        "compte_bancaire": None,
        "solde_conges": solde_restant,
        "jours_pris": jours_utilises,
        "droit_conge_annuel": droit_conge_annuel,
        "annee_reference": annee_courante,
        "dernier_net_paye": float(last_salaire.salaire_net) if last_salaire else None,
        "derniere_periode_paie": (
            last_salaire.periode_fin.isoformat()
            if last_salaire and last_salaire.periode_fin else None
        ),
    }


def _conge_dict(c: Conge) -> Dict[str, Any]:
    """Demande de conge enregistree, telle quelle.

    Le statut remonte dans sa valeur brute d'enum (``en_attente``, ``approuve``,
    ``refuse``...) : l'ecran le traduit, donc la meme donnee s'affiche correctement
    en francais comme en anglais. Un motif absent reste absent, il n'est pas
    remplace par une phrase de remplissage.
    """
    def _valeur(col):
        return col.value if hasattr(col, "value") else col

    employe = c.employe
    return {
        "id": c.id,
        "reference": f"DCG-{c.id}",
        "employe_id": c.employe_id,
        "employe_nom": (employe.full_name or employe.username) if employe else None,
        "type_conge": _valeur(c.type_conge),
        "date_debut": c.date_debut.isoformat() if c.date_debut else None,
        "date_fin": c.date_fin.isoformat() if c.date_fin else None,
        "nombre_jours": c.nombre_jours,
        "statut": _valeur(c.statut),
        "motif": c.motif,
        "date_demande": c.date_demande.isoformat() if c.date_demande else None,
        "approbateur_id": c.approbateur_id,
        "date_approbation": c.date_approbation.isoformat() if c.date_approbation else None,
        "commentaire_approbation": c.commentaire_approbation,
        "motif_refus": c.motif_refus,
    }


MOIS_LIBELLES = [
    "", "Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet",
    "Août", "Septembre", "Octobre", "Novembre", "Décembre",
]


def _bulletin_dict(s: Salaire) -> Dict[str, Any]:
    """Transforme une ligne ``salaires`` reellement enregistree en bulletin.

    Aucune valeur n'est ajoutee : les colonnes absentes de la base donnent 0 ou
    null, jamais une moyenne de marche. Le taux de cotisation est retrouve par
    division des retenues reellement appliquees sur le brut, de sorte que le
    document affiche ce qui a effectivement ete paye et non un taux theorie.
    """
    base = float(s.salaire_base or 0)
    total_primes = sum(
        float(getattr(s, p) or 0)
        for p in (
            "prime_anciennete", "prime_performance", "prime_responsabilite",
            "prime_logement", "prime_transport", "prime_autre",
        )
    )
    heures = float(s.heures_supplementaires or 0)
    indemnite = float(s.taux_horaire_sup or 0)
    cnps = float(s.deductions_cnps or 0)
    irgm = float(s.deductions_impot or 0)
    autres = float(s.deductions_avances or 0) + float(s.autres_deductions or 0)
    brut = base + total_primes + indemnite
    debut = s.periode_debut
    fin = s.periode_fin or debut

    return {
        "id": s.id,
        "reference": f"SAL-{s.id}",
        "employe_id": s.employe_id,
        "periode": f"{debut.year}-{debut.month:02d}" if debut else None,
        "mois": debut.month if debut else None,
        "mois_libelle": MOIS_LIBELLES[debut.month] if debut and debut.month else None,
        "annee": debut.year if debut else None,
        "periode_debut": debut.isoformat() if debut else None,
        "periode_fin": fin.isoformat() if fin else None,
        "salaire_base": base,
        "heures_supplementaires": heures,
        "indemnite_heures_sup": indemnite,
        "primes": total_primes,
        "salaire_brut": round(brut, 2),
        "cotisations_cnps": round(cnps, 2),
        "retenues_fiscales": round(irgm, 2),
        "autres_deductions": round(autres, 2),
        "total_deductions": round(cnps + irgm + autres, 2),
        "taux_cnps": round(cnps / brut, 4) if brut else None,
        "net_a_payer": float(s.salaire_net or 0),
        "statut": s.statut,
        "date_paiement": s.date_paiement.isoformat() if s.date_paiement else None,
        "devise": s.devise,
    }


@router.get("/portail/bulletins")
def get_portail_bulletins(
    db: Session = Depends(get_db),
    current_user: User = Depends(resolve_rh_user)
):
    """Bulletins de paie reellement enregistres pour le salarie connecte.

    La liste est vide tant qu'aucune fiche n'a ete creee par la paie : rien
    n'est invente pour remplir l'ecran. L'appel equivaut a
    ``GET /rh/paie/bulletin`` limite a soi-meme.
    """
    salaires = db.query(Salaire).filter(
        Salaire.employe_id == current_user.id
    ).order_by(Salaire.periode_fin.desc()).all()
    return [_bulletin_dict(s) for s in salaires]


@router.get("/portail/bulletins/{bulletin_id}/telecharger")
def telecharger_bulletin(
    bulletin_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(resolve_rh_user)
):
    """Bulletin imprimable etabli sur la ligne ``salaires`` designee.

    Le document ne peut representer que ce qui a ete paye : chaque montant est
    lu sur l'enregistrement, la reference du bulletin est resolue en cle
    primaire et la fiche d'un autre salarie renvoie un 404. Une fiche absente
    vaut mieux qu'un document de complaisance.

    La mention « signe electriquement » a ete retiree : aucune signature
    electronique n'est apposee par l'application. Le cachet et la signature de
    la DRH restent manuscrits pour que le bulletin fasse foi.
    """
    cle = bulletin_id.strip().upper().replace("SAL-", "").replace("PAY-", "")
    try:
        numero = int(cle)
    except ValueError:
        raise HTTPException(
            status_code=404,
            detail="Reference de bulletin non reconnue : aucun enregistrement correspondant.",
        )

    salaire = db.query(Salaire).filter(
        Salaire.id == numero,
        Salaire.employe_id == current_user.id,
    ).first()
    if not salaire:
        raise HTTPException(
            status_code=404,
            detail="Aucun bulletin de paie a ce numero pour votre compte.",
        )

    b = _bulletin_dict(salaire)

    def _mt(v: float) -> str:
        return f"{float(v or 0):,.0f}".replace(",", " ")

    def _col(v: float) -> str:
        return _mt(v) if v else "&mdash;"

    lignes = [
        ("Salaire de base", b["salaire_base"], 0.0),
        ("Indemnite d'heures supplementaires", b["indemnite_heures_sup"], 0.0),
        ("Primes et avantages", b["primes"], 0.0),
        ("Cotisations CNPS salariales", 0.0, b["cotisations_cnps"]),
        ("Impot general sur le revenu (IRGM)", 0.0, b["retenues_fiscales"]),
        ("Autres retenues (avances, divers)", 0.0, b["autres_deductions"]),
    ]
    lignes_html = "\n".join(
        '          <tr><td>{}</td><td class="text-right">{}</td>'
        '<td class="text-right">{}</td></tr>'.format(
            libelle, _col(gain), _col(retenue)
        )
        for libelle, gain, retenue in lignes
    )

    comp = current_user.company
    raison_sociale = escape((comp.nom if comp else None) or "Employeur non rattache a ce compte")
    identifiants = " &bull; ".join(x for x in [
        (f"Forme : {escape(comp.legal_form)}" if comp and comp.legal_form else None),
        (f"Capital : {escape(comp.capital_social)}" if comp and comp.capital_social else None),
        (f"RCCM : {escape(comp.rccm)}" if comp and comp.rccm else None),
        (f"NUI : {escape(comp.tax_id)}" if comp and comp.tax_id else None),
        (escape(comp.adresse) if comp and comp.adresse else None),
    ] if x) or "Identifiants legaux de l'employeur non renseignes dans la fiche entreprise."

    taux_cnps_affiche = (
        f"{b['taux_cnps'] * 100:.2f} %" if b["taux_cnps"] else "non decompte"
    )
    periode = escape(b["periode"] or "periode indeterminée")
    nom_salarie = escape(current_user.full_name or current_user.username)
    matricule = escape(current_user.matricule or "non attribue")
    poste = escape(current_user.job_title or "non renseigne")
    cnps_salarie = "non renseigné par la DRH"
    banque = "compte bancaire non renseigne"
    date_paiement = escape(b["date_paiement"] or "date de paiement non renseignée")
    statut = escape(b["statut"] or "inconnu")

    html_content = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
      <meta charset="UTF-8">
      <title>Bulletin de paie {b['reference']} - {nom_salarie}</title>
      <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 40px; color: #1e293b; }}
        .header {{ display: flex; justify-content: space-between; border-bottom: 2px solid #0f766e; padding-bottom: 15px; }}
        .company {{ font-size: 20px; font-weight: bold; color: #0f766e; }}
        .legal {{ font-size: 12px; color: #64748b; margin-top: 6px; max-width: 480px; }}
        .badge {{ background: #f0fdf4; color: #166534; padding: 4px 12px; border-radius: 9999px; font-weight: bold; border: 1px solid #bbf7d0; }}
        .emp-box {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 15px; margin: 20px 0; display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 13px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 13px; }}
        th, td {{ border: 1px solid #cbd5e1; padding: 10px; text-align: left; }}
        th {{ background: #f1f5f9; font-weight: bold; }}
        .text-right {{ text-align: right; }}
        .total-box {{ margin-top: 20px; background: #f8fafc; border-top: 3px solid #0f766e; padding: 15px; font-size: 16px; font-weight: bold; display: flex; justify-content: space-between; }}
        .signature {{ margin-top: 48px; display: flex; justify-content: space-between; font-size: 13px; }}
        .signature div {{ width: 45%; }}
        .signature .line {{ border-bottom: 1px solid #94a3b8; height: 60px; margin-bottom: 6px; }}
        .note {{ margin-top: 32px; font-size: 11px; color: #64748b; }}
      </style>
    </head>
    <body>
      <div class="header">
        <div>
          <div class="company">{raison_sociale}</div>
          <div class="legal">{identifiants}</div>
        </div>
        <div style="text-align: right;">
          <span class="badge">BULLETIN DE PAIE</span>
          <div style="font-size: 12px; color: #64748b; margin-top: 8px;">Reference : {escape(b['reference'])}</div>
          <div style="font-size: 12px; color: #64748b;">Periode : {periode}</div>
        </div>
      </div>

      <div class="emp-box">
        <div><strong>Salarie :</strong> {nom_salarie}</div>
        <div><strong>Matricule :</strong> {matricule}</div>
        <div><strong>Emploi :</strong> {poste}</div>
        <div><strong>N&deg; securite sociale :</strong> {escape(cnps_salarie)}</div>
        <div><strong>Mode de reglement :</strong> {escape(banque)}</div>
        <div><strong>Statut du paiement :</strong> {statut}</div>
      </div>

      <table>
        <thead>
          <tr>
            <th>Designation des elements de remuneration</th>
            <th class="text-right">Gains (XAF)</th>
            <th class="text-right">Retenues (XAF)</th>
          </tr>
        </thead>
        <tbody>
{lignes_html}
        </tbody>
      </table>

      <div class="total-box">
        <span>Salaire brut : {_mt(b['salaire_brut'])} XAF &nbsp;|&nbsp; Retenues : {_mt(b['total_deductions'])} XAF</span>
        <span style="color: #0f766e;">NET A PAYER : {_mt(b['net_a_payer'])} XAF</span>
      </div>

      <div class="signature">
        <div>
          <div class="line"></div>
          Signature et cachet de l'employeur
        </div>
        <div>
          <div class="line"></div>
          Remis au salarie le {date_paiement}
        </div>
      </div>

      <div class="note">
        Bulletin etabli a partir des donnees enregistrees dans le module Paie
        (table <code>salaires</code>, ligne n&deg; {numero}). Cotisations
        CNPS constatees sur cette fiche : {taux_cnps_affiche}. En l'absence de
        signature manuscrite et de cachet, le present document n'a pas valeur
        d'attestation.
      </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@router.get("/portail/calendrier-paie")
def get_calendrier_paie(
    db: Session = Depends(get_db),
    current_user: User = Depends(resolve_rh_user)
):
    """Calendrier de paie etabli sur les versements reellement enregistres.

    La date de prochaine paie n'est pas une convention affichee : elle est
    projettee a partir des jours de paiement constates dans la table
    ``salaires`` pour l'entreprise du salarie. Sans aucun versement enregistre,
    ``prochaine_paie`` reste null et le message l'explique, plutot que
    d'annoncer un virement bancaire invente (banque, heure, telecompensation).

    Les fetes chomees et payees listees sont les fetes a date fixe du Code du
    travail camerounais ; les fetes mobiles (Paques, Ascension, Pentecote, Aï-el
    Kébir, Fin Ramadan) dependent du calendrier lunaire et ne sont pas calculées
    ici.
    """
    today = date.today()

    jour_paiement = db.query(Salaire).join(User, User.id == Salaire.employe_id).filter(
        Salaire.date_paiement.isnot(None)
    )
    if not current_user.is_superuser:
        jour_paiement = jour_paiement.filter(User.company_id == current_user.company_id)
    versements = jour_paiement.all()

    jours_observes = sorted({v.date_paiement.day for v in versements})
    dernier = max((v.date_paiement for v in versements), default=None)

    prochaine = None
    if jours_observes:
        jour_cible = jours_observes[len(jours_observes) // 2]
        mois, annee = today.month, today.year
        candidate = date(annee, mois, min(jour_cible, calendar.monthrange(annee, mois)[1]))
        if candidate <= today:
            mois += 1
            if mois > 12:
                mois, annee = 1, annee + 1
            candidate = date(annee, mois, min(jour_cible, calendar.monthrange(annee, mois)[1]))
        prochaine = {
            "date": candidate.isoformat(),
            "jours_restants": (candidate - today).days,
            "jour_paiement_constate": jour_cible,
            "base": "jour median des versements enregistres",
        }

    return {
        "annee": today.year,
        "entreprise": current_user.company.nom if current_user.company else None,
        "fiches_enregistrees": len(versements),
        "jours_paiement_observes": jours_observes,
        "derniere_date_paiement": dernier.isoformat() if dernier else None,
        "prochaine_paie": prochaine,
        "message": (
            None if versements
            else "Aucun versement de salaire enregistre : aucune date de paie ne peut etre annoncee."
        ),
        "jours_feries_cameroun": [
            {"date": f"{today.year}-01-01", "nom": "Jour de l'An", "statut": "Chômé et payé"},
            {"date": f"{today.year}-02-11", "nom": "Fête de la Jeunesse", "statut": "Chômé et payé"},
            {"date": f"{today.year}-05-01", "nom": "Fête du Travail", "statut": "Chômé et payé"},
            {"date": f"{today.year}-05-20", "nom": "Fête Nationale de l'Unité", "statut": "Chômé et payé"},
            {"date": f"{today.year}-08-15", "nom": "Assomption", "statut": "Chômé et payé"},
            {"date": f"{today.year}-11-01", "nom": "Toussaint", "statut": "Chômé et payé"},
            {"date": f"{today.year}-12-25", "nom": "Noël", "statut": "Chômé et payé"},
        ],
        "fetes_mobiles_incluses": False,
    }


@router.get("/portail/conges")
def get_mes_conges(
    db: Session = Depends(get_db),
    current_user: User = Depends(resolve_rh_user)
):
    """Demandes de conge reellement deposees par le salarie connecte.

    Liste vide tant que rien n'a ete depose : aucune demande historique n'est
    generee pour meubler l'historique.
    """
    conges = db.query(Conge).filter(
        Conge.employe_id == current_user.id
    ).order_by(Conge.date_debut.desc()).all()
    return [_conge_dict(c) for c in conges]


@router.post("/portail/conges", status_code=status.HTTP_201_CREATED)
def soumettre_demande_conge_portail(
    payload: PortailDemandeCongeIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(resolve_rh_user)
):
    """Depose la demande de conge du salarie connecte dans la table ``conges``.

    La reponse est la ligne reellement enregistree, serialisee par
    ``_conge_dict`` : le contrat est identique a celui de
    ``GET /portail/conges``, donc l'historique affiche immediatement la demande
    fraiche sans modele intermediaire. Le motif reste vide si le salarie ne l'a
    pas rempli : rien n'est invente a sa place.
    """
    if payload.date_fin < payload.date_debut:
        raise HTTPException(status_code=400, detail="La date de fin ne peut pas être antérieure à la date de début.")

    # Calcul du nombre de jours demandes, puis estimation des jours ouvrables
    # (seuls les jours de travail comptent dans le droit a conge).
    delta_days = (payload.date_fin - payload.date_debut).days + 1
    jours_ouvrables = max(1, int(delta_days * 5 / 7))

    conge_type_enum = TypeConge.CONGE_ANNUEL
    t_str = payload.type_conge.lower()
    if "maladie" in t_str:
        conge_type_enum = TypeConge.CONGE_MALADIE
    elif "maternite" in t_str:
        conge_type_enum = TypeConge.CONGE_MATERNITE
    elif "paternite" in t_str:
        conge_type_enum = TypeConge.CONGE_PATERNITE
    elif "sans" in t_str or "solde" in t_str:
        conge_type_enum = TypeConge.CONGE_SANS_SOLDE
    elif "familial" in t_str or "exceptionnel" in t_str:
        conge_type_enum = TypeConge.CONGE_EXCEPTIONNEL

    nouvelle_demande = Conge(
        employe_id=current_user.id,
        type_conge=conge_type_enum,
        date_debut=payload.date_debut,
        date_fin=payload.date_fin,
        nombre_jours=jours_ouvrables,
        statut=StatutConge.EN_ATTENTE,
        motif=(payload.motif or "").strip() or None,
        date_demande=date.today()
    )
    db.add(nouvelle_demande)
    db.commit()
    db.refresh(nouvelle_demande)

    enregistre = _conge_dict(nouvelle_demande)
    enregistre["jours_ouvrables_estimes"] = jours_ouvrables
    enregistre["message"] = (
        "Demande enregistree et transmise a votre responsable N+1 et a la DRH "
        "pour decision."
    )
    return enregistre


def _racine_depot() -> Path:
    """Dossier de depot autorise pour les pieces du dossier salarie.

    `chemin_fichier` n'est pas une URL : c'est un chemin de stockage. Il n'est
    jamais renvoye tel quel a l'ecran, et il n'est lu que sous cette racine --
    sinon un chemin du type ../../.env permettrait de lire n'importe quel
    fichier du serveur depuis le portail salarie.
    """
    return Path(settings.UPLOAD_DIR).resolve()


def _chemin_document(d: DocumentEmploye):
    """Chemin absolu du fichier, ou None s'il n'est pas servable.

    Un chemin hors du depot autorise ou un fichier disparu du disque n'est pas
    une erreur a afficher sur la liste : la piece reste visible -- elle est bien
    verse au dossier -- elle n'est simplement pas telechargeable.
    """
    brut = (d.chemin_fichier or "").strip()
    if not brut:
        return None
    racine = _racine_depot()
    chemin = Path(brut)
    if not chemin.is_absolute():
        chemin = racine / chemin
    try:
        resolus = chemin.resolve()
        resolus.relative_to(racine)
    except (OSError, ValueError):
        return None
    return resolus if resolus.is_file() else None


def _acces_document_portail(d: DocumentEmploye):
    """(telechargeable, url) : l'URL interne n'existe que si le fichier existe."""
    if _chemin_document(d) is None:
        return False, None
    return True, f"/api/v1/rh/portail/documents/{d.id}/fichier"


@router.get("/portail/documents")
def get_portail_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(resolve_rh_user)
):
    """Documents RH reellement verses au dossier du salarie connecte.

    La liste est construite sur la table ``documents_employe`` : une piece
    absente du dossier n'apparait pas, et aucun document type (reglement
    interieur, convention collective) n'est annonce comme telechargeable sans
    fichier reel derriere.

    L'attestation de travail est le seul document delivre par l'application
    elle-meme : elle n'est proposee que si un contrat est enregistre, faute de
    quoi elle affirmerait une relation de travail que rien n'etablit.
    """
    fichiers = db.query(DocumentEmploye).filter(
        DocumentEmploye.employe_id == current_user.id
    ).order_by(DocumentEmploye.date_emission.desc()).all()

    documents: List[Dict[str, Any]] = []
    for d in fichiers:
        accessible, url = _acces_document_portail(d)
        documents.append({
            "id": d.id,
            "reference": f"DOC-{d.id}",
            "titre": f"{d.type_document} / {d.nom_fichier}",
            "type": d.type_document,
            "nom_fichier": d.nom_fichier,
            # Aucun numero ni organisme emetteur n'est verse au dossier : la base
            # ne stocke que le chemin de la piece. Rien n'est invente pour
            # remplir la carte, l'ecran affiche « non renseigne ».
            "numero_document": None,
            "organisme_emetteur": None,
            "date_emission": d.date_emission.isoformat() if d.date_emission else None,
            "date_expiration": d.date_expiration.isoformat() if d.date_expiration else None,
            "statut": None,
            "commentaire": None,
            "telechargeable": accessible,
            "url_telechargement": url,
            "raison_indisponibilite": None if accessible else "FICHIER_NON_DISPONIBLE",
        })

    contrat = db.query(ContratTravail).filter(
        ContratTravail.employe_id == current_user.id
    ).order_by(ContratTravail.date_debut.desc()).first()

    documents.append({
        "id": "ATTESTATION-TRAVAIL",
        "reference": "ATTESTATION-TRAVAIL",
        # Pas de libelle francais : l'ecran traduit le type de piece, conforme
        # a la regle FR/EN. Seules les pieces versees ont un titre calcule.
        "titre": None,
        "type": "ATTESTATION",
        "nom_fichier": None,
        "numero_document": None,
        "organisme_emetteur": (current_user.company.nom if current_user.company else None),
        "date_emission": date.today().isoformat(),
        "date_expiration": None,
        "statut": "en_cours" if contrat else "indisponible",
        "telechargeable": bool(contrat),
        "url_telechargement": (
            "/api/v1/rh/portail/documents/attestation-travail" if contrat else None
        ),
        "commentaire": None,
        # Cle machine traduite par l'ecran : « aucun contrat enregistre », sans
        # texte francais embarque dans l'API.
        "raison_indisponibilite": None if contrat else "AUCUN_CONTRAT_ENREGISTRE",
    })

    return documents


@router.get("/portail/documents/{document_id}/fichier")
def telecharger_document_portail(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(resolve_rh_user)
):
    """Renvoie une piece du dossier DU SALARIE CONNECTE, et d'elle seule.

    Le filtre porte sur employe_id dans la requete meme : un salarie qui connait
    l'identifiant numerique du diplome d'un collegue recoit un 404, pas le
    document. Aucun chemin n'est accepte depuis l'URL, seul celui enregistre par
    la DRH est lu, et uniquement sous le depot autorise.
    """
    d = db.query(DocumentEmploye).filter(
        DocumentEmploye.id == document_id,
        DocumentEmploye.employe_id == current_user.id,
    ).first()
    if not d:
        raise HTTPException(
            status_code=404,
            detail="Document absent de votre dossier. Rapprochez la DRH.")

    chemin = _chemin_document(d)
    if chemin is None:
        raise HTTPException(
            status_code=404,
            detail=("Le fichier de cette piece n'est plus accessible sur le "
                    "serveur : rapprochez la DRH pour un nouveau depot."))

    type_mime, _ = mimetypes.guess_type(str(chemin))
    return FileResponse(
        path=str(chemin),
        media_type=type_mime or "application/octet-stream",
        filename=d.nom_fichier,
    )


@router.get("/portail/documents/attestation-travail")
def telecharger_attestation_travail(
    db: Session = Depends(get_db),
    current_user: User = Depends(resolve_rh_user)
):
    """Attestation de travail etablie sur les seules donnees RH enregistrees.

    Un contrat absent renvoie un 404 : l'application ne peut pas attester une
    relation de travail qu'aucune piece du dossier n'etablit. Les informations
    qui n'ont jamais ete saisies (numero CNPS, compte bancaire) portent la
    mention « non renseigne » au lieu d'un numero calcule de toute piece.

    Le nom du signataire et la mention « certifie electroniquement » ont ete
    retires : aucun mecanisme de signature electronique n'existe ici. Le cadre
    reste ouvert au cachet et a la signature manuscrite du responsable RH, seuls
    elements qui font foi.
    """
    contrat = db.query(ContratTravail).filter(
        ContratTravail.employe_id == current_user.id
    ).order_by(ContratTravail.date_debut.desc()).first()
    if not contrat:
        raise HTTPException(
            status_code=404,
            detail=(
                "Aucun contrat de travail enregistre a votre nom : l'attestation "
                "ne peut pas etre delivree. Rapprochez la DRH."
            ),
        )

    comp = current_user.company
    raison_sociale = escape(
        (comp.nom if comp else None) or "Employeur non rattache a un compte entreprise"
    )
    mentions_legales = " &bull; ".join(x for x in [
        (f"Forme : {escape(comp.legal_form)}" if comp and comp.legal_form else None),
        (f"Capital : {escape(comp.capital_social)}" if comp and comp.capital_social else None),
        (f"RCCM : {escape(comp.rccm)}" if comp and comp.rccm else None),
        (f"NIF : {escape(comp.tax_id)}" if comp and comp.tax_id else None),
        (escape(comp.adresse) if comp and comp.adresse else None),
    ] if x) or "Identifiants legaux de l'employeur non renseignes dans la fiche entreprise."

    nom_salarie = escape(current_user.full_name or current_user.username)
    matricule = escape(current_user.matricule or "non attribue")
    poste = escape(current_user.job_title or contrat.poste or "non renseigne")
    departement = escape(contrat.departement or (
        current_user.department.nom if current_user.department else None) or "non renseigne")
    type_contrat = escape(contrat.type_contrat or "non renseigne")
    horaire = escape(contrat.horaire_travail or "non renseigne")
    lieu = escape(contrat.lieu_travail or "non renseigne")
    date_embauche = contrat.date_debut.strftime("%d/%m/%Y") if contrat.date_debut else "non renseignee"
    date_fin_contrat = (
        contrat.date_fin.strftime("%d/%m/%Y")
        if contrat.date_fin else "sans terme (contrat a duree indeterminee)"
    )
    statut_contrat = escape(contrat.statut or "actif")
    cnps = "non renseigne par la DRH"
    today_str = date.today().strftime("%d/%m/%Y")
    ville_entreprise = (comp.ville if comp else None)
    ligne_fait = (
        f"Fait &agrave; {escape(ville_entreprise)}, le {today_str}"
        if ville_entreprise else f"Fait le {today_str}"
    )
    statut_contrat_norme = (contrat.statut or "actif").strip().lower()
    if statut_contrat_norme == "actif":
        phrase_emple = (
            "Est li&eacute;(&eacute;) &agrave; la soci&eacute;t&eacute; par un contrat "
            "en cours d'ex&eacute;cution depuis le "
            f"{escape(date_embauche)}, et y occupe &agrave; ce jour le poste "
            "mentionn&eacute; ci-dessus."
        )
    else:
        phrase_emple = (
            "A &eacute;t&eacute; li&eacute;(&eacute;) &agrave; la soci&eacute;t&eacute; par un "
            f"contrat portant le statut « {escape(contrat.statut)} », avec une "
            f"date d'effet au {escape(date_embauche)}."
        )

    html_content = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
      <meta charset="UTF-8">
      <title>Attestation de travail - {nom_salarie}</title>
      <style>
        body {{ font-family: 'Times New Roman', Times, serif; margin: 60px 80px; color: #000; line-height: 1.6; }}
        .header {{ text-align: center; border-bottom: 2px solid #000; padding-bottom: 20px; }}
        .title {{ font-size: 24px; font-weight: bold; text-decoration: underline; margin: 40px 0; text-align: center; }}
        .content {{ font-size: 16px; text-align: justify; }}
        .signature-block {{ margin-top: 60px; display: flex; justify-content: space-between; align-items: flex-end; }}
        .signature-line {{ border-bottom: 1px solid #000; height: 70px; width: 260px; margin-bottom: 8px; }}
        .legal {{ font-size: 12px; color: #444; margin-top: 6px; }}
        .fields {{ margin-left: 30px; }}
        .fields div {{ margin-bottom: 4px; }}
        .note {{ margin-top: 36px; font-size: 11px; color: #444; }}
      </style>
    </head>
    <body>
      <div class="header">
        <h2 style="margin: 0; text-transform: uppercase;">{raison_sociale}</h2>
        <p class="legal" style="margin: 5px 0;">{mentions_legales}</p>
      </div>

      <div class="title">ATTESTATION DE TRAVAIL</div>

      <div class="content">
        <p>La soci&eacute;t&eacute; <em>{raison_sociale}</em> atteste que&nbsp;:</p>
        
        <div class="fields">
          <div><strong>Nom et pr&eacute;noms&nbsp;:</strong> {nom_salarie}</div>
          <div><strong>Matricule entreprise&nbsp;:</strong> {matricule}</div>
          <div><strong>Num&eacute;ro s&eacute;curit&eacute; sociale (CNPS)&nbsp;:</strong> {escape(cnps)}</div>
          <div><strong>Fonction / poste&nbsp;:</strong> {poste}</div>
          <div><strong>D&eacute;partement&nbsp;:</strong> {departement}</div>
          <div><strong>Type de contrat&nbsp;:</strong> {type_contrat} (statut&nbsp;: {statut_contrat})</div>
          <div><strong>Date d'embauche&nbsp;:</strong> {date_embauche}</div>
          <div><strong>Fin de contrat pr&eacute;vue&nbsp;:</strong> {escape(date_fin_contrat)}</div>
          <div><strong>Dur&eacute;e hebdomadaire&nbsp;:</strong> {horaire}</div>
          <div><strong>Lieu de travail&nbsp;:</strong> {lieu}</div>
        </div>

        <p>{phrase_emple}</p>

        <p>La présente attestation lui est délivrée à sa demande pour servir et valoir ce que de droit.</p>

        <p style="margin-top: 30px;">{ligne_fait}.</p>
      </div>

      <div class="signature-block">
        <div>
          <div class="signature-line"></div>
          Cachet et signature de l'employeur
        </div>
        <div style="text-align: right;">
          <div class="signature-line"></div>
          Le responsable des ressources humaines
        </div>
      </div>

      <div class="note">
        Document &eacute;tabli &agrave; partir des donn&eacute;es enregistr&eacute;es dans le
        module RH (table <code>contrats_travail</code>, r&eacute;f&eacute;rence
        n&deg;&nbsp;{contrat.id}). L'application n'appose aucune signature
        &eacute;lectronique&nbsp;: la pr&eacute;sente attestation n'a de valeur
        qu'apr&egrave;s signature manuscrite et apposition du cachet de
        l'employeur.
      </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


# ============================================================================
# ⚙️ ANCIENS ENDPOINTS RH EXISTANTS (PRÉSERVÉS ET SÉCURISÉS)
# ============================================================================

# ============ CONGÉS ============
def _refus_metier(exc: ValueError) -> HTTPException:
    """Une regle metier refusee n'est pas un plantage technique.

    Un solde insuffisant, un type de conge inconnu ou une heure de saisie
    invalide sont des refus attendus, donc explicites : sans ce pont, ils
    remontaient en 500 "Internal Server Error", l'ecran ne pouvant rien afficher
    d'exploitable alors que la raison tenait en une phrase.
    """
    return HTTPException(status_code=400, detail=str(exc))


@router.post("/conges", response_model=CongeResponse, status_code=status.HTTP_201_CREATED)
def demander_conge(
    conge: CongeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(resolve_rh_user)
):
    """Submit leave request"""
    try:
        return CongeService.demander_conge(
            db, current_user.id, conge.type_conge, conge.date_debut,
            conge.date_fin, conge.motif
        )
    except ValueError as exc:
        raise _refus_metier(exc)


@router.get("/conges")
def lister_conges(
    statut: Optional[str] = None,
    employe_id: Optional[int] = None,
    annee: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(resolve_rh_user),
):
    """Demandes de conge enregistrees, limitees a l'entreprise du demandeur.

    Un salarie ordinaire (niveau 3) ne voit que ses propres demandes ; un chef
    de departement, un admin entreprise ou la DRH voit celles de son tenant.
    La liste est vide si aucune demande n'a ete deposee : aucun historique
    n'est genere pour meubler l'ecran.
    """
    q = db.query(Conge).join(User, User.id == Conge.employe_id)
    scope = _employee_scope_company_id(current_user)
    if scope is not None:
        q = q.filter(User.company_id == scope)
    if not current_user.is_superuser and (current_user.role_level or 99) >= 3:
        q = q.filter(Conge.employe_id == current_user.id)
    if employe_id:
        q = q.filter(Conge.employe_id == employe_id)
    if statut:
        # Le filtre passe par l'enum : une valeur inconnue ne part pas en requete
        # (elle leverait LookupError au bind, donc en 500).
        try:
            q = q.filter(Conge.statut == StatutConge(statut.strip().lower()))
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="statut de conge inconnu : "
                       + ", ".join(s.value for s in StatutConge))
    if annee:
        q = q.filter(extract("year", Conge.date_debut) == annee)
    conges = q.order_by(Conge.date_debut.desc()).offset(skip).limit(limit).all()
    return [_conge_dict(c) for c in conges]


@router.get("/conges/solde/{employe_id}/{annee}", response_model=SoldeCongeResponse)
def obtenir_solde_conge(
    employe_id: int,
    annee: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(resolve_rh_user)
):
    """Get leave balance for employee and year"""
    return CongeService.calculer_solde_conge(db, employe_id, annee)


@router.put("/conges/{conge_id}/approuver", response_model=CongeResponse)
def approuver_conge(
    conge_id: int,
    commentaire: str = "",
    db: Session = Depends(get_db),
    current_user: User = Depends(resolve_rh_user)
):
    """Approve leave request"""
    try:
        return CongeService.approuver_conge(db, conge_id, current_user.id, commentaire)
    except ValueError as exc:
        raise _refus_metier(exc)


@router.put("/conges/{conge_id}/rejeter", response_model=CongeResponse)
def rejeter_conge(
    conge_id: int,
    motif_refus: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(resolve_rh_user)
):
    """Reject leave request"""
    try:
        return CongeService.rejeter_conge(db, conge_id, current_user.id, motif_refus)
    except ValueError as exc:
        raise _refus_metier(exc)


class DecisionCongePortail(BaseModel):
    """Decision sur une demande de conge, telle que la saisit l'ecran.

    `commentaire` reste libre : approuver comme refuser sans commentaire est
    admis. L'application n'oblige personne a produire une raison qu'il n'a pas.
    """
    approuve: bool
    commentaire: Optional[str] = None


@router.post("/conges/{conge_id}/decision", response_model=CongeResponse)
def decider_conge_depuis_portail(
    conge_id: int,
    data: DecisionCongePortail,
    db: Session = Depends(get_db),
    current_user: User = Depends(resolve_rh_user)
):
    """Meme decision, sous la forme du bouton flottant et du portail RH.

    ``chef_personnel`` expose deja ``POST /conges/{id}/decision`` pour le N+1.
    Cette route rend la meme decision au salarie habilite : l'ecran n'a pas a
    connaitre la casquette de qui clique, et une liste qui n'offre que la
    consultation laisserait le bouton "Approuver" sans destination.
    """
    try:
        if data.approuve:
            return CongeService.approuver_conge(
                db, conge_id, current_user.id, data.commentaire)
        return CongeService.rejeter_conge(
            db, conge_id, current_user.id, data.commentaire)
    except ValueError as exc:
        raise _refus_metier(exc)


# ============ ABSENCES ============
@router.post("/absences", response_model=AbsenceResponse, status_code=status.HTTP_201_CREATED)
def enregistrer_absence(
    absence: AbsenceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(resolve_rh_user)
):
    """Record absence"""
    try:
        return AbsenceService.enregistrer_absence(
            db, current_user.id, absence.type_absence, absence.date_debut,
            absence.date_fin, absence.motif, absence.justifie
        )
    except ValueError as exc:
        raise _refus_metier(exc)


@router.get("/absences/taux/{employe_id}/{mois}/{annee}")
def obtenir_taux_absenteisme(
    employe_id: int,
    mois: int,
    annee: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(resolve_rh_user)
):
    """Calculate absenteeism rate"""
    taux = AbsenceService.calculer_taux_absenteisme(db, employe_id, mois, annee)
    return {"employe_id": employe_id, "mois": mois, "annee": annee, "taux_absenteisme": taux}


# ============ TEMPS DE TRAVAIL ============
@router.post("/pointage/arrivee", response_model=TempsTravailResponse, status_code=status.HTTP_201_CREATED)
def pointer_arrivee(
    date_pointage: date,
    # Heure de saisie "HH:MM" (champ <input type="time"> du portail), pas un
    # horodatage : la colonne est un VARCHAR(5) en base.
    heure_arrivee: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(resolve_rh_user)
):
    """Clock in"""
    try:
        return TempsTravailService.pointer_arrivee(
            db, current_user.id, date_pointage, heure_arrivee)
    except ValueError as exc:
        raise _refus_metier(exc)


@router.post("/pointage/depart", response_model=TempsTravailResponse)
def pointer_depart(
    date_pointage: date,
    heure_depart: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(resolve_rh_user)
):
    """Clock out"""
    try:
        return TempsTravailService.pointer_depart(
            db, current_user.id, date_pointage, heure_depart)
    except ValueError as exc:
        raise _refus_metier(exc)


@router.get("/heures/{employe_id}/{mois}/{annee}", response_model=HeuresMensuellesResponse)
def calculer_heures_mois(
    employe_id: int,
    mois: int,
    annee: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(resolve_rh_user)
):
    """Calculate monthly hours worked"""
    return TempsTravailService.calculer_heures_mois(db, employe_id, mois, annee)


# ============ FORMATIONS ============
@router.post("/formations", response_model=FormationResponse, status_code=status.HTTP_201_CREATED)
def creer_formation(
    formation: FormationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(resolve_rh_user)
):
    """Create training session"""
    return FormationService.creer_formation(
        db, formation.titre, formation.description, formation.date_debut,
        formation.date_fin, formation.duree_heures, formation.cout,
        formation.formateur, formation.lieu, formation.agency_id
    )


@router.post("/formations/{formation_id}/inscrire/{employe_id}", response_model=ParticipationFormationResponse, status_code=status.HTTP_201_CREATED)
def inscrire_formation(
    formation_id: int,
    employe_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(resolve_rh_user)
):
    """Enroll employee in training"""
    try:
        return FormationService.inscrire_employe(db, formation_id, employe_id)
    except ValueError as exc:
        raise _refus_metier(exc)


@router.put("/formations/participations/{participation_id}")
def valider_participation(
    participation_id: int,
    present: bool,
    certificat_obtenu: bool = False,
    commentaire: str = "",
    db: Session = Depends(get_db),
    current_user: User = Depends(resolve_rh_user)
):
    """Validate training participation"""
    try:
        return FormationService.valider_participation(
            db, participation_id, present, certificat_obtenu, commentaire
        )
    except ValueError as exc:
        raise _refus_metier(exc)


@router.get("/formations/expirantes")
def obtenir_formations_expirantes(
    jours_avance: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(resolve_rh_user)
):
    """Get trainings with expiring certifications"""
    return FormationService.obtenir_formations_expirantes(db, jours_avance)


# ============ PERFORMANCE ============
@router.post("/evaluations", response_model=EvaluationPerformanceResponse, status_code=status.HTTP_201_CREATED)
def creer_evaluation(
    evaluation: EvaluationPerformanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(resolve_rh_user)
):
    """Create performance evaluation"""
    return PerformanceService.creer_evaluation(
        db, evaluation.employe_id, evaluation.evaluateur_id,
        evaluation.periode_debut, evaluation.periode_fin,
        evaluation.note_globale, evaluation.commentaires,
        evaluation.objectifs_atteints, evaluation.objectifs_total
    )


@router.get("/evaluations/{employe_id}")
def obtenir_historique_evaluation(
    employe_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(resolve_rh_user)
):
    """Get employee evaluation history"""
    return PerformanceService.obtenir_historique_evaluation(db, employe_id)


# ============ CONTRATS ============
@router.post("/contrats", response_model=ContratTravailResponse, status_code=status.HTTP_201_CREATED)
def creer_contrat(
    contrat: ContratTravailCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(resolve_rh_user)
):
    """Create employment contract"""
    return ContratService.creer_contrat(
        db, contrat.employe_id, contrat.type_contrat, contrat.date_debut,
        contrat.date_fin, contrat.poste, contrat.salaire_base,
        contrat.coefficient, contrat.classification, contrat.periode_essai_jours
    )


@router.get("/contrats/expirants")
def obtenir_contrats_expirants(
    jours_avance: int = 60,
    db: Session = Depends(get_db),
    current_user: User = Depends(resolve_rh_user)
):
    """Get contracts expiring soon"""
    return ContratService.obtenir_contrats_expirants(db, jours_avance)


@router.put("/contrats/{contrat_id}/renouveler", response_model=ContratTravailResponse)
def renouveler_contrat(
    contrat_id: int,
    nouvelle_date_fin: date,
    nouveau_salaire: float = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(resolve_rh_user)
):
    """Renew employment contract"""
    return ContratService.renouveler_contrat(db, contrat_id, nouvelle_date_fin, nouveau_salaire)


# ============ PAIE ============
class FichePaieIn(BaseModel):
    """Saisie d'une fiche de paie.

    Seules les donnees que la paie est censee frapper sont attendues ici : le
    calcul des cotisations sociales et de l'IRGM reste dans ``PaieService``,
    source unique des baremes Cameroun/CEMAC.
    """
    employe_id: int
    mois: int
    annee: int
    salaire_base: float
    heures_supplementaires: float = 0
    primes: List[Dict[str, Any]] = Field(default_factory=list)
    deductions: List[Dict[str, Any]] = Field(default_factory=list)
    date_paiement: Optional[date] = None
    statut: str = "en_attente"


STATUTS_PAIE = ("en_attente", "paye", "annule")

_CATEGORIES_PRIMES = {
    "anciennete": "prime_anciennete",
    "performance": "prime_performance",
    "responsabilite": "prime_responsabilite",
    "logement": "prime_logement",
    "transport": "prime_transport",
}


def _montant(entry: Any) -> float:
    if isinstance(entry, dict):
        return float(entry.get("montant") or 0)
    return float(getattr(entry, "montant", 0) or 0)


def _categorie(entry: Any) -> str:
    if isinstance(entry, dict):
        raw = entry.get("type") or entry.get("type_prime") or entry.get("categorie") or ""
    else:
        raw = getattr(entry, "type", "") or getattr(entry, "type_prime", "") or ""
    return str(raw).strip().lower()


@router.post("/paie/bulletin", status_code=status.HTTP_201_CREATED)
def creer_fiche_paie(
    payload: FichePaieIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(requireRH),
):
    """Calcule puis ENREGISTRE la fiche de paie dans la table ``salaires``.

    La version precedente se bornait a renvoyer le calcul sans jamais ecrire la
    ligne : le portail n'avait donc rien a lister, ce qui avait conduit a
    seeded des bulletins fictifs. La fiche est desormais persistee, une seule
    fois par employe et par periode.

    Les primes saisies sont reparties sur les colonnes dedicatees du modele
    (anciennete, performance, responsabilite, logement, transport) ; une prime
    hors nomenclature est portee en ``prime_autre`` et reste visible sur le
    bulletin. Les deductions suivent la meme logique : « avance » est separe du
    reste.
    """
    if not 1 <= payload.mois <= 12 or not 1900 <= payload.annee <= 2999:
        raise HTTPException(
            status_code=400,
            detail="Periode de paie invalide : mois entre 1 et 12, annee explicite.",
        )
    if payload.statut not in STATUTS_PAIE:
        raise HTTPException(
            status_code=400,
            detail=f"Statut de paie inconnu. Valeurs admises : {', '.join(STATUTS_PAIE)}.",
        )
    if payload.salaire_base < 0:
        raise HTTPException(status_code=400, detail="Le salaire de base ne peut pas etre negatif.")

    employe = db.query(User).filter(User.id == payload.employe_id).first()
    if not employe:
        raise HTTPException(status_code=404, detail="Aucun employe a cet identifiant.")
    scope = _employee_scope_company_id(current_user)
    if scope is not None and employe.company_id != scope:
        raise HTTPException(
            status_code=403,
            detail="Cet employe n'appartient pas a votre entreprise.",
        )

    debut = date(payload.annee, payload.mois, 1)
    fin = date(payload.annee, payload.mois, calendar.monthrange(payload.annee, payload.mois)[1])
    if db.query(Salaire).filter(
        Salaire.employe_id == employe.id,
        Salaire.periode_debut == debut,
    ).first():
        raise HTTPException(
            status_code=409,
            detail=(
                f"Une fiche de paie existe deja pour cet employe sur la periode "
                f"{debut.strftime('%m/%Y')}."
            ),
        )

    calcul = PaieService.preparer_bulletin(
        db, employe.id, payload.mois, payload.annee, payload.salaire_base,
        payload.heures_supplementaires, payload.primes, payload.deductions,
    )

    repartition = {col: 0.0 for col in _CATEGORIES_PRIMES.values()}
    repartition["prime_autre"] = 0.0
    for entry in payload.primes:
        colonne = _CATEGORIES_PRIMES.get(_categorie(entry), "prime_autre")
        repartition[colonne] += _montant(entry)

    avances = 0.0
    autres_retenues = 0.0
    for entry in payload.deductions:
        if "avance" in _categorie(entry):
            avances += _montant(entry)
        else:
            autres_retenues += _montant(entry)

    brut = float(calcul["salaire_brut"])
    cnps = float(calcul["cotisations"]["cnps"])
    irgm = float(calcul["impot_revenu"])

    # Duree reellement pointee sur la periode. L'ancienne valeur (173,33 des
    # qu'une heure supplementaire etait saisie) inscrivait un forfait legal la
    # ou un releve horaires existe : le bulletin affichait alors des heures que
    # personne n'avait pointees. Sans pointage, la colonne reste vide -- une
    # inconnue affichee vaut mieux qu'une moyenne legale presente comme un fait.
    releve_mois = TempsTravailService.calculer_heures_mois(
        db, employe.id, payload.mois, payload.annee)
    heures_pointees = float(releve_mois["heures_travaillees"] or 0)

    fiche = Salaire(
        employe_id=employe.id,
        periode_debut=debut,
        periode_fin=fin,
        salaire_base=payload.salaire_base,
        heures_supplementaires=payload.heures_supplementaires,
        # La colonne porte l'indemnite d'heures sup. (ce que _bulletin_dict relit
        # comme montant) et non un taux : le nom est herite de la base.
        taux_horaire_sup=float(calcul["indemnite_heures_sup"]),
        deductions_cnps=round(cnps, 2),
        deductions_impot=round(irgm, 2),
        deductions_avances=round(avances, 2),
        autres_deductions=round(autres_retenues, 2),
        salaire_net=round(float(calcul["salaire_net"]), 2),
        devise="XAF",
        date_paiement=payload.date_paiement,
        statut=payload.statut,
        nombre_heures_travaillees=heures_pointees or None,
        taux_imposition=round(irgm / brut, 6) if brut else 0,
        **repartition,
    )
    db.add(fiche)
    db.commit()
    db.refresh(fiche)

    bulletin = _bulletin_dict(fiche)
    bulletin["message"] = (
        f"Fiche de paie {debut.strftime('%m/%Y')} enregistree pour "
        f"{employe.full_name or employe.username}."
    )
    return bulletin


@router.get("/paie/bulletin")
def lister_fiches_paie(
    employe_id: Optional[int] = None,
    statut: Optional[str] = None,
    annee: Optional[int] = None,
    mois: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(resolve_rh_user),
):
    """Fiches de paie reellement enregistrees dans l'entreprise du demandeur.

    Le salaire d'un autre tenant n'est jamais accessible : la requete est
    jointee sur ``users.company_id``. Un salarie peut appeler cette route pour
    lui-meme, ce qui remplace le mecanisme de donnees factices qui avait ete
    branche sur le portail.
    """
    q = db.query(Salaire).join(User, User.id == Salaire.employe_id)
    scope = _employee_scope_company_id(current_user)
    if scope is not None:
        q = q.filter(User.company_id == scope)
    if not current_user.is_superuser and (current_user.role_level or 99) >= 3:
        q = q.filter(Salaire.employe_id == current_user.id)
    if employe_id:
        q = q.filter(Salaire.employe_id == employe_id)
    if statut:
        q = q.filter(Salaire.statut == statut.strip().lower())
    if annee:
        q = q.filter(extract("year", Salaire.periode_debut) == annee)
    if mois:
        q = q.filter(extract("month", Salaire.periode_debut) == mois)
    fiches = q.order_by(Salaire.periode_debut.desc()).offset(skip).limit(limit).all()
    return [_bulletin_dict(s) for s in fiches]


# ============ DOCUMENTS EMPLOYÉ ============
@router.post("/documents", response_model=DocumentEmployeResponse, status_code=status.HTTP_201_CREATED)
def ajouter_document(
    document: DocumentEmployeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(resolve_rh_user)
):
    """Add employee document"""
    return DocumentEmployeService.ajouter_document(
        db, document.employe_id, document.type_document,
        document.chemin_fichier, document.date_emission, document.date_expiration
    )


@router.get("/documents/expirants")
def obtenir_documents_expirants(
    jours_avance: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(resolve_rh_user)
):
    """Get documents expiring soon"""
    return DocumentEmployeService.obtenir_documents_expirants(db, jours_avance)


# ============ ORGANIGRAMME ============
@router.post("/organigramme", response_model=OrganigrammeResponse, status_code=status.HTTP_201_CREATED)
def definir_hierarchie(
    org: OrganigrammeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(resolve_rh_user)
):
    """Define employee hierarchy"""
    return OrganigrammeService.definir_hierarchie(
        db, org.employe_id, org.manager_id, org.departement, org.poste
    )


@router.get("/organigramme/subordonnes/{manager_id}")
def obtenir_subordonnes(
    manager_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(resolve_rh_user)
):
    """Get all direct reports of a manager"""
    return OrganigrammeService.obtenir_subordonnes(db, manager_id)


# ============ COMPÉTENCES ============
@router.post("/competences", response_model=CompetenceResponse, status_code=status.HTTP_201_CREATED)
def creer_competence(
    competence: CompetenceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(resolve_rh_user)
):
    """Create skill/competency definition"""
    return CompetenceService.creer_competence(
        db, competence.nom, competence.categorie,
        competence.description, competence.niveau_requis
    )


@router.post("/competences/attribuer", response_model=CompetenceEmployeResponse, status_code=status.HTTP_201_CREATED)
def attribuer_competence(
    competence: CompetenceEmployeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(resolve_rh_user)
):
    """Assign skill to employee"""
    return CompetenceService.attribuer_competence(
        db, competence.employe_id, competence.competence_id,
        competence.niveau, competence.date_evaluation
    )


@router.get("/competences/{employe_id}")
def obtenir_competences_employe(
    employe_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(resolve_rh_user)
):
    """Get all employee skills"""
    return CompetenceService.obtenir_competences_employe(db, employe_id)


# ============================================================================
# 👥 EMPLOYES (annuaire du personnel, scope entreprise)
# ============================================================================
def _employee_scope_company_id(user: User) -> Optional[int]:
    """None => all companies (super admin). Otherwise the caller's company."""
    return None if user.is_superuser else user.company_id


def _employee_dict(u: User) -> Dict[str, Any]:
    return {
        "id": u.id,
        "username": u.username,
        "email": u.email,
        "full_name": u.full_name or u.username,
        "phone": u.phone,
        "is_active": u.is_active,
        "role_level": u.role_level,
        "role": get_user_role_label(u),
        "company_id": u.company_id,
        "department_id": u.department_id,
        "department": (u.department.nom if getattr(u, "department", None) else None),
        "avatar_url": u.avatar_url,
        "language": u.language,
        "timezone": u.timezone,
        "last_login": u.last_login.isoformat() if u.last_login else None,
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


@router.get("/employes/me")
def employe_actuel(
    db: Session = Depends(get_db),
    current_user: User = Depends(resolve_rh_user),
):
    """Profil du collaborateur connecte."""
    return _employee_dict(current_user)


@router.get("/employes")
def lister_employes(
    search: Optional[str] = None,
    department_id: Optional[int] = None,
    include_inactive: bool = False,
    skip: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(resolve_rh_user),
):
    """Annuaire du personnel, strictement limite a l'entreprise du demandeur."""
    query = db.query(User)
    scope = _employee_scope_company_id(current_user)
    if scope is not None:
        query = query.filter(User.company_id == scope)
    if not include_inactive:
        query = query.filter(User.is_active.is_(True))
    if department_id is not None:
        query = query.filter(User.department_id == department_id)
    if search:
        s = f"%{search.strip()}%"
        query = query.filter(or_(User.username.ilike(s), User.email.ilike(s), User.full_name.ilike(s)))
    total = query.count()
    users = query.order_by(User.full_name.asc().nullslast()).offset(skip).limit(limit).all()
    return {"items": [_employee_dict(u) for u in users], "total": total}


@router.get("/employes/{employe_id}")
def detail_employe(
    employe_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(resolve_rh_user),
):
    """Fiche d'un employe (scope entreprise respecte)."""
    emp = db.query(User).filter(User.id == employe_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employe introuvable")
    scope = _employee_scope_company_id(current_user)
    if scope is not None and emp.company_id != scope:
        raise HTTPException(status_code=403, detail="Employe hors de votre entreprise")
    return _employee_dict(emp)


@router.post("/employes/import-excel", status_code=status.HTTP_202_ACCEPTED)
def import_employes_excel(
    db: Session = Depends(get_db),
    current_user: User = Depends(resolve_rh_user),
):
    """Import massif d'employes depuis Excel  non implemente cote serveur.

    Reponse honnete 202 ``pending`` (aucune donnee inventee) tant que l'import
    n'est pas branche, pour que l'ecran n'affiche pas une erreur 404/500.
    """
    return {
        "accepted": False,
        "pending": True,
        "message": "L'import Excel des employes n'est pas encore actif cote serveur.",
    }
