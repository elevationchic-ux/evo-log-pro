"""Router FastAPI  Portail B2B Client EVO-LOG.

Toutes les reponses proviennent des tables metier reelles du tenant :
``clients``, ``dossiers_transit_avance``, ``missions``, ``factures``,
``paiements``, ``tarifs``, ``cotations_devis``, ``conteneurs_cycle`` et
``preferences_notification``.

Aucun jeu de donnees de demonstration : le service
``app.services.b2b_portal_service`` contenait des listes codées en dur
(DOS-2026-00841, MSKU9823412, factures et parcours inventes). Il n'est plus
appele ici. Quand une information n'existe pas en base, elle est absente de la
reponse (ou la reponse est 400/404) : jamais remplacee par une valeur devinee.
"""
from fastapi import APIRouter, Depends, Query, Body, HTTPException
from sqlalchemy import func, or_
from sqlalchemy.orm import Session
from datetime import datetime, date as date_type, time as time_type
import re
import uuid

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.tiers import Client
from app.models.acconage import Conteneur
from app.models.finance import Facture, Paiement, FactureStatus, PaiementStatus
from app.models.transport import Mission, MissionStatus
from app.models.transit_avance import DossierTransitAvance
from app.models.conteneur_cycle import ConteneurCycle
from app.models.gap_bridge import Tarif
from app.models.new_k_modules import CotationDevis
from app.models.notifications import PreferenceNotification

router = APIRouter()

# Modes de paiement proposés par le portail -> valeur persistee dans
# paiements.mode_paiement. Un mode inconnu est refuse plutot que rangé en « autre ».
MODES_PAIEMENT = {
    "MTN_MOMO": "mobile_money",
    "ORANGE_MONEY": "mobile_money",
    "VIREMENT_SGBC": "virement",
    "VIREMENT": "virement",
    "CHEQUE": "cheque",
    "ESPECE": "espece",
}


def _id_enterprise(current_user: User):
    """Tenant authentifie : seule source de la portee des ecritures."""
    return getattr(current_user, "company_id", None)


def _client_ou_erreur(db: Session, client_id) -> Client:
    """Le client du portail doit exister reellement dans le tenant.

    Plus d'identifiant code en dur cote frontend : sans ``client_id`` valide,
    on renvoie 404 avec la liste des clients accessibles plutot que d'inventer
    un compte ou de retourner un tableau vide presente comme un succes.
    """
    try:
        cid = int(client_id)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=400,
            detail="client_id manquant ou invalide : selectionnez un client reel du compte.",
        )
    client = db.query(Client).filter(Client.id == cid).first()
    if not client:
        accessibles = db.query(Client.id, Client.name).limit(20).all()
        raise HTTPException(
            status_code=404,
            detail={
                "message": f"Client {cid} introuvable pour ce compte.",
                "clients_accessibles": [
                    {"id": c.id, "name": c.name} for c in accessibles
                ],
            },
        )
    return client


def _float(v):
    return float(v) if v is not None else None


def _dt(v):
    return v.isoformat() if v else None


# ============ DOSSIERS DU CLIENT ============
@router.get("/dossiers", summary="Lister les dossiers du client B2B connecté")
def get_dossiers(
    client_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Dossiers reellement ouverts pour ce client : transit + missions routieres.

    ``progression_pct`` n'est PAS renvoyee : aucune colonne ne porte un
    pourcentage d'avancement en base, le calculer serait inventer un etat.
    """
    client = _client_ou_erreur(db, client_id)

    dossiers = (
        db.query(DossierTransitAvance)
        .filter(DossierTransitAvance.client_id == client.id)
        .order_by(DossierTransitAvance.id.desc())
        .all()
    )
    missions = (
        db.query(Mission)
        .filter(Mission.client_id == client.id)
        .order_by(Mission.id.desc())
        .all()
    )
    # Mission n'a pas de relation ORM vers les conteneurs : on resout la table
    # ``conteneurs`` (cible de la cle etrangere conteneur_id) en une seule
    # requete, et le numero reste absent s'il n'est pas rattache.
    ids_conteneurs = sorted({m.conteneur_id for m in missions if m.conteneur_id})
    numeros = {}
    if ids_conteneurs:
        numeros = {
            c.id: c.numero
            for c in db.query(Conteneur).filter(Conteneur.id.in_(ids_conteneurs)).all()
        }

    items = [
        {
            "id": f"TRT-{d.id}",
            "origine": "TRANSIT",
            "reference": d.numero_dossier,
            "type": (d.type_transit.value if hasattr(d.type_transit, "value") else d.type_transit),
            "regime_douanier": (
                d.regime_douanier.value if hasattr(d.regime_douanier, "value") else d.regime_douanier
            ),
            "description": d.marchandise,
            "statut": d.statut,
            "date_ouverture": _dt(d.date_ouverture),
            "date_cloture": _dt(d.date_cloture),
            "numero_connaisse": d.numero_connaisse,
            "poids_brut_kg": _float(d.poids_brut),
            "montant_total_xaf": _float(d.montant_total),
        }
        for d in dossiers
    ] + [
        {
            "id": f"MSN-{m.id}",
            "origine": "TRANSPORT",
            "reference": m.reference,
            "type": m.type_mission,
            "description": (
                f"{m.point_depart or 'depart non renseigne'} -> "
                f"{m.point_arrivee or 'arrivee non renseignee'}"
            ),
            "statut": m.statut.value if hasattr(m.statut, "value") else m.statut,
            "date_debut_prevue": _dt(m.date_debut_prevue),
            "date_fin_reelle": _dt(m.date_fin_reelle),
            "conteneur": numeros.get(m.conteneur_id),
            "numero_bl": m.numero_bl,
            "distance_km": _float(m.distance_km),
        }
        for m in missions
    ]

    return {
        "client_id": client.id,
        "client_nom": client.name,
        "total": len(items),
        "dossiers": items,
    }


# ============ FACTURES DU CLIENT ============
@router.get("/factures", summary="Lister les factures du client B2B")
def get_factures(
    client_id: int = Query(...),
    statut: str = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Factures emises pour le client, solde calcule sur les paiements persistes."""
    client = _client_ou_erreur(db, client_id)

    q = db.query(Facture).filter(Facture.client_id == client.id)
    if statut:
        q = q.filter(Facture.statut == statut)
    factures = q.order_by(Facture.id.desc()).all()

    items = []
    for f in factures:
        # Somme reelle des paiements CONFIRMES uniquement : un paiement en
        # attente de confirmation externe ne reduit pas le solde.
        paye = (
            db.query(func.coalesce(func.sum(Paiement.montant), 0))
            .filter(Paiement.facture_id == f.id, Paiement.statut == PaiementStatus.CONFIRME)
            .scalar()
        )
        paye = float(paye or 0)
        ttc = float(f.montant_ttc or 0)
        items.append({
            "id": f.id,
            "numero_facture": f.numero_facture,
            "date_emission": f.date_emission.isoformat() if f.date_emission else None,
            "date_echeance": f.date_echeance.isoformat() if f.date_echeance else None,
            "montant_ht": _float(f.montant_ht),
            "montant_tva": _float(f.montant_tva),
            "montant_ttc": ttc,
            "montant_paye": paye,
            "solde_du_xaf": round(max(ttc - paye, 0), 2),
            "devise": f.devise,
            "statut": f.statut.value if hasattr(f.statut, "value") else f.statut,
            "notes": f.notes,
        })

    impayees = [i for i in items if i["statut"] in (
        FactureStatus.EMISE.value, FactureStatus.PAYEE_PARTIELLEMENT.value,
        FactureStatus.RETARD.value,
    )]
    return {
        "client_id": client.id,
        "total": len(items),
        "factures": items,
        "total_en_attente_xaf": round(sum(i["solde_du_xaf"] for i in impayees), 2),
        "nb_a_regler": len(impayees),
    }


# ============ COTATION INSTANTANEE ============
def _reference_unique(db: Session, modele, colonne, prefix: str) -> str:
    """Reference ``PREFIX-AAAAMMJJ-XXXXXX`` verifiee contre la base."""
    base = f"{prefix}-{datetime.now().strftime('%Y%m%d')}"
    for _ in range(50):
        cand = f"{base}-{uuid.uuid4().hex[:6].upper()}"
        if not db.query(modele.id).filter(colonne == cand).first():
            return cand
    raise HTTPException(status_code=500, detail="Generation de reference impossible")


@router.post("/quotes", summary="Calculer et enregistrer une cotation fret & transit")
def calculate_quote(
    payload: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Chiffre la demande a partir de la grille tarifaire PERSISTEE du tenant.

    Les prix ne viennent d'aucune constante du code : chaque ligne correspond a
    une ligne active de la table ``tarifs``. Si aucune grille ne couvre le
    service demande, la reponse est 400 : un devis ne peut pas etre fabrique.
    """
    service = (payload.get("service_type") or payload.get("type_service") or "").strip().upper()
    if not service:
        raise HTTPException(status_code=400, detail="service_type requis.")
    quantite = int(payload.get("container_count") or payload.get("nombre_conteneurs") or 0)
    if quantite <= 0:
        raise HTTPException(status_code=400, detail="container_count doit etre un entier > 0.")

    lignes_tarif = (
        db.query(Tarif)
        .filter(func.upper(Tarif.categorie) == service)
        .filter((Tarif.is_active.is_(True)) | (Tarif.is_active.is_(None)))
        .all()
    )
    extras = [s for s in (payload.get("services_additionnels") or []) if s]
    for extra in extras:
        lignes_tarif += (
            db.query(Tarif)
            .filter(func.upper(Tarif.code) == str(extra).strip().upper())
            .filter((Tarif.is_active.is_(True)) | (Tarif.is_active.is_(None)))
            .all()
        )

    if not lignes_tarif:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Aucune ligne tarifaire active ne couvre '{service}' dans la table "
                "tarifs : renseignez la grille commerciale avant d'editer un devis."
            ),
        )

    lignes = []
    for t in lignes_tarif:
        prix = float(t.prix or 0)
        tva_pct = float(t.tva or 0)
        # Facture par unite de conteneur quand l'unite l'indique, sinon forfait.
        par_unite = (t.unite or "").strip().lower() in ("conteneur", "tc", "unite", "each", "u")
        qte = quantite if par_unite else 1
        ht = round(prix * qte, 2)
        tva = round(ht * tva_pct / 100, 2)
        lignes.append({
            "code": t.code,
            "designation": t.designation,
            "categorie": t.categorie,
            "unite": t.unite,
            "quantite": qte,
            "prix_unitaire_ht": prix,
            "tva_pct": tva_pct,
            "montant_ht": ht,
            "montant_tva": tva,
            "montant_ttc": round(ht + tva, 2),
        })

    total_ht = round(sum(l["montant_ht"] for l in lignes), 2)
    total_tva = round(sum(l["montant_tva"] for l in lignes), 2)
    cotation = CotationDevis(
        company_id=_id_enterprise(current_user),
        reference=_reference_unique(db, CotationDevis, CotationDevis.reference, "DEV"),
        client_nom=(payload.get("client_nom") or "").strip(),
        origine=payload.get("port_of_loading") or payload.get("origine") or "",
        destination=payload.get("final_destination") or payload.get("destination") or "",
        nature_fret=service,
        montant_estime_xaf=round(total_ht + total_tva, 2),
        detail_lignes={
            "lignes": lignes,
            "container_type": payload.get("container_type"),
            "container_count": quantite,
            "incoterm": payload.get("incoterm"),
            "urgence": payload.get("urgence"),
            "cargo_nature": payload.get("cargo_nature"),
            "services_additionnels": extras,
        },
        client_id=payload.get("client_id"),
        statut="SOUMIS",
    )
    db.add(cotation)
    db.commit()
    db.refresh(cotation)

    return {
        "id": cotation.id,
        "reference": cotation.reference,
        "statut": cotation.statut,
        "service_type": service,
        "lignes": lignes,
        "total_ht": total_ht,
        "total_tva": total_tva,
        "total_ttc": cotation.montant_estime_xaf,
        "devise": "XAF",
        "source": "tarifs (grille persistee du tenant)",
        "valabilite": "Devis soumis : aucun tarif n'est garanti, la grille peut evoluer.",
    }


@router.get("/quotes", summary="Lister les cotations du client")
def list_quotes(
    client_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Devis reellement enregistres pour ce client (table cotations_devis)."""
    client = _client_ou_erreur(db, client_id)
    rows = (
        db.query(CotationDevis)
        .filter(CotationDevis.client_id == client.id)
        .order_by(CotationDevis.id.desc())
        .all()
    )
    return {
        "client_id": client.id,
        "total": len(rows),
        "devis": [
            {
                "id": c.id,
                "reference": c.reference,
                "service_type": c.nature_fret,
                "origine": c.origine,
                "destination": c.destination,
                "montant_estime_xaf": _float(c.montant_estime_xaf),
                "statut": c.statut,
                "created_at": _dt(c.created_at),
                "lignes": (c.detail_lignes or {}).get("lignes", []) if c.detail_lignes else [],
            }
            for c in rows
        ],
    }


# ============ E-BOOKING ENLEVEMENT ============
@router.post("/booking", summary="Créer une réservation e-Booking d'enlèvement conteneur")
def create_booking(
    payload: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Enleve le conteneur en creant une MISSION REELLE dans le module transport.

    Le creneau demande doit etre resolvable : date + plage « HH:MM-HH:MM ».
    Aucun horodatage n'est invente, aucun numero de bon n'est simule : la
    reference retournee est celle de la mission persistee.
    """
    date_enlevement = payload.get("date_enlevement")
    creneau = (payload.get("creneau_horaire") or "").strip()
    terminal = (payload.get("terminal") or "").strip()
    if not date_enlevement or not creneau or not terminal:
        raise HTTPException(
            status_code=400,
            detail="Champs requis : terminal, date_enlevement et creneau_horaire (ex. 08:00-10:00).",
        )

    client = _client_ou_erreur(db, payload.get("client_id"))

    try:
        jour = datetime.strptime(str(date_enlevement)[:10], "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="date_enlevement doit etre au format AAAA-MM-JJ.")

    m = re.match(r"^(\d{1,2}):(\d{2})\s*-\s*(\d{1,2}):(\d{2})$", creneau)
    if not m:
        raise HTTPException(
            status_code=400,
            detail="creneau_horaire invalide : format attendu HH:MM-HH:MM.",
        )
    debut = datetime.combine(jour, time_type(int(m.group(1)), int(m.group(2))))
    fin = datetime.combine(jour, time_type(int(m.group(3)), int(m.group(4))))
    if fin <= debut:
        raise HTTPException(
            status_code=400,
            detail="creneau_horaire incoherent : l'heure de fin doit suivre l'heure de debut.",
        )

    numero_conteneur = (payload.get("numero_conteneur") or "").strip().upper()
    conteneur_id = None
    if numero_conteneur:
        # La cle etrangere missions.conteneur_id pointe vers la table
        # ``conteneurs`` (parc acconage), pas vers conteneurs_cycle.
        trouve = (
            db.query(Conteneur).filter(Conteneur.numero == numero_conteneur).first()
        )
        conteneur_id = trouve.id if trouve else None

    mission = Mission(
        company_id=_id_enterprise(current_user),
        reference=_reference_unique(db, Mission, Mission.reference, "BKG"),
        client_id=client.id,
        conteneur_id=conteneur_id,
        type_mission="enlevement",
        statut=MissionStatus.PLANIFIEE,
        date_debut_prevue=debut,
        date_fin_prevue=fin,
        point_depart=terminal,
        point_arrivee=(payload.get("destination") or "").strip() or None,
        numero_bl=(payload.get("numero_bl") or "").strip() or None,
        notes=(
            f"Reservation e-Booking portail B2B du {jour.isoformat()} creneau {creneau}. "
            + (f"Conteneur {numero_conteneur} " if numero_conteneur else "Conteneur non renseigne. ")
            + (
                "rattache au parc conteneurs."
                if conteneur_id
                else ": aucun conteneur porte ce numero en base, lien non etabli."
            )
        ),
    )
    db.add(mission)
    db.commit()
    db.refresh(mission)

    return {
        "id": mission.id,
        "reference": mission.reference,
        "statut": mission.statut.value if hasattr(mission.statut, "value") else mission.statut,
        "terminal": terminal,
        "date_enlevement": jour.isoformat(),
        "creneau_horaire": creneau,
        "conteneur_rattache": bool(conteneur_id),
        "numero_conteneur": numero_conteneur or None,
        "note": (
            "Reservation enregistree comme mission de transport. L'horaire est une "
            "demande : il n'est pas confirme par le terminal tant que l'exploitation "
            "ne l'a pas valide."
        ),
    }


# ============ TRACKING ============
@router.get("/tracking/{query}", summary="Tracking conteneur ISO 6346 ou numéro de B/L")
def track_cargo(
    query: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Suivi multi-jalons d'une marchandise, uniquement ce qui est relie en base.

    S'appuie sur ``consigner_dossier_marchandise`` : les etapes que le schema ne
    relie pas au conteneur sont signalees, rien n'est devine. Une reference
    inconnue renvoie 404 (pas un faux parcours).
    """
    from app.services.dossier_marchandise import consigner_dossier_marchandise

    ref = (query or "").strip()
    if len(ref) < 4:
        raise HTTPException(status_code=400, detail="Reference trop courte : 4 caracteres minimum.")

    try:
        dossier = consigner_dossier_marchandise(db, numero_conteneur=ref, numero_bl=ref)
    except HTTPException as exc:
        if exc.status_code == 404:
            raise HTTPException(
                status_code=404,
                detail=f"Aucune marchandise portant la reference '{ref}' dans ce compte.",
            )
        raise

    conteneur = (
        db.query(ConteneurCycle).filter(ConteneurCycle.numero == ref.upper()).first()
    )
    if conteneur:
        dossier["conteneur"] = {
            "numero": conteneur.numero,
            "type": conteneur.type_conteneur.value if hasattr(conteneur.type_conteneur, "value") else conteneur.type_conteneur,
            "taille_pieds": conteneur.taille_pieds,
            "proprietaire": conteneur.proprietaire,
            "compagnie": conteneur.compagnie,
            "etat": conteneur.etat.value if hasattr(conteneur.etat, "value") else conteneur.etat,
            "date_derniere_inspection": (
                conteneur.date_derniere_inspection.isoformat()
                if conteneur.date_derniere_inspection else None
            ),
        }

    # Surestaries : la franchise s'appuie sur des dates et des taux reellement
    # parametres. Sans donnee d'entree, le champ reste absent au lieu d'afficher
    # un compte a rebours fabrique.
    missions_liees = db.query(Mission).filter(
        or_(
            Mission.numero_bl == ref,
            Mission.reference == ref,
        )
    ).order_by(Mission.id.desc()).all()
    dossier["missions"] = [
        {
            "reference": ms.reference,
            "statut": ms.statut.value if hasattr(ms.statut, "value") else ms.statut,
            "point_depart": ms.point_depart,
            "point_arrivee": ms.point_arrivee,
            "date_debut_prevue": _dt(ms.date_debut_prevue),
            "date_fin_reelle": _dt(ms.date_fin_reelle),
        }
        for ms in missions_liees
    ]
    return dossier


# ============ PAIEMENT ============
@router.post("/payments/checkout", summary="Enregistrer une demande de paiement facture")
def process_checkout(
    payload: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Enregistre une DEMANDE de paiement, ne simule aucun debit.

    Une passerelle Mobile Money / CB reelle n'est pas branchee : la ligne est
    ecrite en ``en_attente`` et la facture garde son solde. Le cachet
    « payee_partiellement » / « payee » ne peut venir que d'une confirmation
    externe reelle, jamais de ce endpoint.
    """
    facture_id = payload.get("facture_id") or payload.get("invoice_id")
    mode = (payload.get("mode_paiement") or payload.get("method") or "").strip().upper()
    if not facture_id or not mode:
        raise HTTPException(
            status_code=400,
            detail="Champs requis : facture_id et mode_paiement (MTN_MOMO, ORANGE_MONEY, VIREMENT).",
        )
    if mode not in MODES_PAIEMENT:
        raise HTTPException(
            status_code=400,
            detail=f"Mode de paiement inconnu : {mode}. Modes acceptes : {sorted(MODES_PAIEMENT)}.",
        )

    facture = db.query(Facture).filter(Facture.id == int(facture_id)).first()
    if not facture:
        raise HTTPException(status_code=404, detail="Facture introuvable.")
    if facture.statut in (FactureStatus.ANNULEE, FactureStatus.BROUILLON):
        raise HTTPException(
            status_code=400,
            detail=f"Facture au statut {facture.statut} : aucun paiement enregistrable.",
        )

    paye = float(
        db.query(func.coalesce(func.sum(Paiement.montant), 0))
        .filter(Paiement.facture_id == facture.id, Paiement.statut == PaiementStatus.CONFIRME)
        .scalar() or 0
    )
    solde = round(float(facture.montant_ttc or 0) - paye, 2)
    if solde <= 0:
        raise HTTPException(status_code=400, detail="Cette facture est deja reglee en base.")

    montant = payload.get("montant_xaf")
    montant = solde if montant in (None, "") else round(float(montant), 2)
    if montant <= 0 or montant > solde:
        raise HTTPException(
            status_code=400,
            detail=f"Montant hors solde : le reste du est {solde} {facture.devise}.",        )

    telephone = (payload.get("phone") or payload.get("telephone") or "").strip()
    paiement = Paiement(
        company_id=_id_enterprise(current_user),
        facture_id=facture.id,
        montant=montant,
        date_paiement=date_type.today(),
        mode_paiement=MODES_PAIEMENT[mode],
        reference=f"INT-{uuid.uuid4().hex[:10].upper()}",
        statut=PaiementStatus.EN_ATTENTE,
        notes=(
            f"Initie depuis le portail B2B (mode {mode})"
            + (f" sur le numero {telephone}" if telephone else "")
            + ". Aucun debit certifie : en attente de la confirmation du prestataire."
        ),
    )
    db.add(paiement)
    db.commit()
    db.refresh(paiement)

    return {
        "id": paiement.id,
        "reference": paiement.reference,
        "facture_id": facture.id,
        "numero_facture": facture.numero_facture,
        "montant": float(paiement.montant),
        "statut": paiement.statut.value if hasattr(paiement.statut, "value") else paiement.statut,
        "solde_restant": round(solde - montant, 2),
        "avertissement": (
            "Paiement enregistré en attente : aucune passerelle bancaire ou Mobile Money "
            "n'a confirme le debit. Le solde de la facture ne sera reduit qu'a la confirmation."
        ),
    }


# ============ PREFERENCES DE NOTIFICATION ============
@router.get("/notifications/preferences", summary="Consulter les préférences de notifications")
def get_notification_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Canaux reellement enregistres pour l'utilisateur connecte.

    La table ``preferences_notification`` est portee par l'utilisateur : le
    ``client_id`` passe par le frontend n'est pas une cle de lecture (il ne
    correspond a rien en base), il est donc ignore plutot que subit.
    """
    rows = (
        db.query(PreferenceNotification)
        .filter(PreferenceNotification.utilisateur_id == current_user.id)
        .order_by(PreferenceNotification.categorie, PreferenceNotification.type_canal)
        .all()
    )
    return {
        "utilisateur_id": current_user.id,
        "total": len(rows),
        "preferences": [
            {
                "id": p.id,
                "type_canal": p.type_canal,
                "categorie": p.categorie,
                "active": bool(p.active),
                "frequence": p.frequence,
                "heures_silence": p.heures_silence,
                "jours_silence": p.jours_silence,
            }
            for p in rows
        ],
        "note": (
            "Aucune preference par defaut n'est fabriquee : si la liste est vide, "
            "l'utilisateur n'a encore enregistre aucun canal."
        ),
    }


@router.put("/notifications/preferences", summary="Mettre à jour les préférences de notifications")
def update_notification_preferences(
    payload: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Enregistre (ou met a jour) un canal de notification reellement demande.

    Le format attendu est ``{"preferences": [{"type_canal": "email",
    "categorie": "statut_dossier", "active": true, "frequence": "immediat"}]}``.
    Un canal absent de la requete n'est pas modifie : aucune reecriture globale.
    """
    entrees = payload.get("preferences")
    if not isinstance(entrees, list) or not entrees:
        raise HTTPException(
            status_code=400,
            detail="payload.preferences : liste non vide attendue "
                   "[{type_canal, categorie, active, frequence}].",
        )

    enregistrees = []
    for e in entrees:
        canal = (e.get("type_canal") or "").strip().lower()
        categorie = (e.get("categorie") or "").strip().lower()
        if not canal or not categorie:
            raise HTTPException(
                status_code=400,
                detail="Chaque preference exige type_canal et categorie.",
            )
        ligne = (
            db.query(PreferenceNotification)
            .filter(
                PreferenceNotification.utilisateur_id == current_user.id,
                func.lower(PreferenceNotification.type_canal) == canal,
                func.lower(PreferenceNotification.categorie) == categorie,
            )
            .first()
        )
        if not ligne:
            ligne = PreferenceNotification(
                utilisateur_id=current_user.id,
                type_canal=canal,
                categorie=categorie,
            )
            db.add(ligne)
        ligne.active = bool(e.get("active", True))
        if e.get("frequence"):
            ligne.frequence = str(e["frequence"]).strip().lower()
        if "heures_silence" in e:
            ligne.heures_silence = e["heures_silence"]
        if "jours_silence" in e:
            ligne.jours_silence = e["jours_silence"]
        enregistrees.append((ligne, canal, categorie))

    db.commit()
    for ligne, _, _ in enregistrees:
        db.refresh(ligne)

    return {
        "total": len(enregistrees),
        "preferences": [
            {
                "id": ligne.id,
                "type_canal": ligne.type_canal,
                "categorie": ligne.categorie,
                "active": bool(ligne.active),
                "frequence": ligne.frequence,
            }
            for ligne, _, _ in enregistrees
        ],
    }
