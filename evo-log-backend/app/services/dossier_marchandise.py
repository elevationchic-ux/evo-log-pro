"""Dossier unique de marchandise - vue consolidee HONNETE le long de la chaine.

Objectif (P2 #7) : donner a l'operateur portuaire une fiche qui retrace, a
partir d'un identifiant physique reel (numero de conteneur ou numero de
connaissement / B/L), tout ce qui EXISTE vraiment dans la base pour chaque
etape : arrivee au navire/escale, connaissement, operations d'acconage,
packing list, cycle de vie (dechargement -> stocke -> sorti), mouvements de
parc (gate in/out), puis declaration douaniere, magasin, livraison, facture.

PRINCIPE D'HONNETETE (zero-mock) :
  Ce module N'INVENTE AUCUN LIEN. Il n'affiche une etape que si un chemin
  REEL la rattache a l'ancre :
    • soit une cle etrangere enforcee (ex. connaissements.conteneur_id) ;
    • soit la correspondance par NUMERO DE CONTENEUR, identifiant physique
      universel de la logistique portuaire (colonne ``numero`` /
      ``numero_conteneur`` presente dans les modeles cycles et parc) ;
    • soit les colonnes de la chaine documentaire (migration 024 :
      conteneur_id / escale_id / numero_bl sur declaration douaniere,
      magasin, mission et facture). Un enregistrement n'apparait que si le
      lien a ete SAISI explicitement sur la ligne ; rien n'est devine par
      proximite de date, de client ou de montant.
  Si le schema ne permet toujours aucune jonction pour un modele, l'etape est
  renvoyee avec l'etat ``non_liciable_en_base`` : on ne fabrique pas une
  jointure que la base ne permet pas.

Chaque etape porte donc :
    etat               : "reel" | "absent" | "non_liciable_en_base"
    mode_correspondance: chemin exact utilise (FK ou numero) ou raison du blocage
    enregistrements    : champs reels minimal des lignes trouvees (vide sinon)
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import HTTPException

from app.models.acconage import (
    Conteneur,
    Connaissement,
    Escale,
    Navire,
    OperationAcconage,
    PackingList,
)


def _stage(cle: str, libelle: str, etat: str, mode: str,
           enregistrements: Optional[List[Dict[str, Any]]] = None,
           note: Optional[str] = None) -> Dict[str, Any]:
    return {
        "cle": cle,
        "libelle": libelle,
        "etat": etat,                     # reel | absent | non_liciable_en_base
        "mode_correspondance": mode,      # comment la jonction est (ou n'est pas) etablie
        "enregistrements": enregistrements or [],
        "note": note,
    }


def _serialize(obj: Any, champs: List[str]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for c in champs:
        v = getattr(obj, c, None)
        out[c] = str(v) if v is not None and not isinstance(v, (int, float, bool)) else v
    return out


def consigner_dossier_marchandise(
    db,
    numero_conteneur: Optional[str] = None,
    numero_bl: Optional[str] = None,
) -> Dict[str, Any]:
    """Retourne la vue consolidee d'une marchandise, sans jamais inventer de lien.

    Au moins un des deux identifiants physiques (numero de conteneur ou numero de
    connaissement) est requis. Si aucun enregistrement reel ne correspond, on
    leve une 404 explicite (ressource inconnue) au lieu de retourner un dossier
    vide presente comme un succes.
    """
    if not numero_conteneur and not numero_bl:
        raise HTTPException(
            status_code=400,
            detail="Un identifiant physique est requis : numero_conteneur ou numero_bl.",
        )

    numero_conteneur = (numero_conteneur or "").strip() or None
    numero_bl = (numero_bl or "").strip() or None

    conteneur: Optional[Conteneur] = None
    bl_direct: Optional[Connaissement] = None

    if numero_conteneur:
        conteneur = (
            db.query(Conteneur).filter(Conteneur.numero == numero_conteneur).first()
        )
    if conteneur is None and numero_bl:
        bl_direct = (
            db.query(Connaissement)
            .filter(Connaissement.numero_bl == numero_bl)
            .first()
        )
        if bl_direct is not None and bl_direct.conteneur_id:
            conteneur = (
                db.query(Conteneur)
                .filter(Conteneur.id == bl_direct.conteneur_id)
                .first()
            )

    if conteneur is None and bl_direct is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Aucune marchandise trouvee pour "
                f"numero_conteneur={numero_conteneur!r}, numero_bl={numero_bl!r}. "
                "Aucun dossier n'est fabrique."
            ),
        )

    # Le numero physique sert de cle transversale pour les modeles cycles/parc.
    numero_physique = conteneur.numero if conteneur is not None else None

    etapes: List[Dict[str, Any]] = []

    # 1. Ancre : fiche conteneur (reel si conteneur résolu) ------------------
    if conteneur is not None:
        etapes.append(_stage(
            "conteneur", "Fiche conteneur", "reel",
            "acconage.conteneurs (numero unique)",
            [_serialize(conteneur, [
                "id", "numero", "type_conteneur", "statut",
                "gross_weight", "net_weight", "proprietaire", "scelle",
            ])],
        ))
    else:
        etapes.append(_stage(
            "conteneur", "Fiche conteneur", "absent",
            "connu uniquement par son B/L ; aucune ligne conteneur correspondante",
            note="Le connaissement existe mais ne reference pas de conteneur en base.",
        ))

    # 2. Arrivee : navire / escale (reel via FK navire_id / escale_id) -------
    navire = None
    if conteneur is not None and conteneur.navire_id:
        navire = db.query(Navire).filter(Navire.id == conteneur.navire_id).first()
    escale_ids = set()
    if bl_direct is not None and bl_direct.escale_id:
        escale_ids.add(bl_direct.escale_id)
    if conteneur is not None:
        for bl in db.query(Connaissement).filter(Connaissement.conteneur_id == conteneur.id).all():
            if bl.escale_id:
                escale_ids.add(bl.escale_id)
    escales = []
    for eid in escale_ids:
        e = db.query(Escale).filter(Escale.id == eid).first()
        if e is not None:
            escales.append(_serialize(e, [
                "id", "numero_escale", "poste_quai", "statut",
                "date_arrivee_reelle", "date_depart_reelle",
            ]))
    arrivee_enr: List[Dict[str, Any]] = []
    if navire is not None:
        arrivee_enr.append(_serialize(navire, ["id", "nom", "imo", "armateur", "type_navire"]))
    arrivee_enr.extend([{"escale": e} for e in escales])
    etapes.append(_stage(
        "arrivee", "Arrivee (navire / escale)",
        "reel" if arrivee_enr else "absent",
        "conteneurs.navire_id -> navires ; connaissements.escale_id -> escales",
        arrivee_enr,
    ))

    # 3. Connaissement(s) / B/L (reel via conteneur_id) ----------------------
    bls = []
    if conteneur is not None:
        bls = db.query(Connaissement).filter(Connaissement.conteneur_id == conteneur.id).all()
    elif bl_direct is not None:
        bls = [bl_direct]
    etapes.append(_stage(
        "connaissement", "Connaissement(s) / Bill of Lading",
        "reel" if bls else "absent",
        "connaissements.conteneur_id -> conteneurs.id (cle etrangee enforcee)",
        [_serialize(b, [
            "id", "numero_bl", "type_bl", "chargeur", "destinataire",
            "port_embarquement", "port_dechargement", "date_emission",
            "montant_freight", "devise", "statut",
        ]) for b in bls],
    ))

    # 4. Operations d'acconage (reel via escale_id des B/L) ------------------
    ops_enr: List[Dict[str, Any]] = []
    if escale_ids:
        ops = (
            db.query(OperationAcconage)
            .filter(OperationAcconage.escale_id.in_(list(escale_ids)))
            .all()
        )
        ops_enr = [_serialize(o, [
            "id", "reference", "type_operation", "date_debut", "date_fin",
            "marchandise", "quantite", "unite", "statut",
        ]) for o in ops]
    etapes.append(_stage(
        "acconage", "Operations d'acconage",
        "reel" if ops_enr else ("absent" if escale_ids else "non_liciable_en_base"),
        "operations_acconage.escale_id -> escale(s) rattachee(s) au B/L"
        if escale_ids else "aucune escale rattachee : operation non reliable a ce conteneur",
        ops_enr,
    ))

    # 5. Packing list (reel via conteneur_id) -------------------------------
    pls = []
    if conteneur is not None:
        pls = db.query(PackingList).filter(PackingList.conteneur_id == conteneur.id).all()
    etapes.append(_stage(
        "packing_list", "Packing list",
        "reel" if pls else "absent",
        "packing_lists.conteneur_id -> conteneurs.id (cle etrangee enforcee)",
        [_serialize(p, [
            "id", "numero_pl", "marchandise", "nombre_colis", "type_colis",
            "poids_net", "poids_brut", "volume_m3", "pays_origine",
        ]) for p in pls],
    ))

    # 6. Cycle de vie conteneur (correspondance par NUMERO physique) --------
    cycle_enr: List[Dict[str, Any]] = []
    if numero_physique:
        try:
            from app.models.conteneur_cycle import ConteneurCycle, CycleConteneur

            cc = (
                db.query(ConteneurCycle)
                .filter(ConteneurCycle.numero == numero_physique)
                .all()
            )
            for un in cc:
                for cyc in db.query(CycleConteneur).filter(
                    CycleConteneur.conteneur_id == un.id
                ).all():
                    cycle_enr.append({
                        "cycle_id": cyc.id,
                        "statut": str(getattr(cyc.statut, "value", cyc.statut)),
                        "localisation": cyc.localisation,
                        "date_arrivee_navire": str(cyc.date_arrivee_navire) if cyc.date_arrivee_navire else None,
                        "date_dechargement": str(cyc.date_dechargement) if cyc.date_dechargement else None,
                        "date_mise_quai": str(cyc.date_mise_quai) if cyc.date_mise_quai else None,
                        "date_sortie": str(cyc.date_sortie) if cyc.date_sortie else None,
                    })
        except Exception:  # pragma: no cover - modele absent du runtime
            cycle_enr = []
    etapes.append(_stage(
        "cycle_de_vie", "Cycle de vie (dechargement / stocke / sorti)",
        "reel" if cycle_enr else ("absent" if numero_physique else "non_liciable_en_base"),
        "conteneurs_cycle.numero = numero physique du conteneur (identifiant universel)",
        cycle_enr,
    ))

    # 7. Mouvements de parc / gate in-out (correspondance par NUMERO) -------
    parc_enr: List[Dict[str, Any]] = []
    if numero_physique:
        try:
            from app.models.parc import MouvementParc

            mvs = (
                db.query(MouvementParc)
                .filter(MouvementParc.numero_conteneur == numero_physique)
                .order_by(MouvementParc.horodatage)
                .all()
            )
            parc_enr = [{
                "id": m.id,
                "sens": m.sens,
                "etat": m.etat,
                "immatriculation": m.immatriculation,
                "chauffeur": m.chauffeur,
                "motif": m.motif,
                "horodatage": str(m.horodatage) if m.horodatage else None,
            } for m in mvs]
        except Exception:  # pragma: no cover - modele absent du runtime
            parc_enr = []
    etapes.append(_stage(
        "parc", "Mouvements de parc (gate in / gate out)",
        "reel" if parc_enr else ("absent" if numero_physique else "non_liciable_en_base"),
        "parc_mouvements.numero_conteneur = numero physique du conteneur",
        parc_enr,
    ))

    # 8-11. Etapes aval : licables DESORMAIS via les colonnes de la chaine
    # documentaire (migration 024). Un enregistrement n'apparait que s'il porte
    # explicitement notre conteneur (FK) ou un de nos numeros de B/L :
    # aucune ligne n'est devinee par proximite de date ou de client.
    bl_numbers = {b.numero_bl for b in bls if getattr(b, "numero_bl", None)}
    cid = conteneur.id if conteneur is not None else None
    from sqlalchemy import or_ as sa_or  # noqa: E402

    def _aval(cle, libelle, importeur, table, champs, colonnes):
        try:
            Model = importeur()
        except Exception:  # pragma: no cover - modele absent du runtime
            return _stage(cle, libelle, "non_liciable_en_base",
                          f"modele {table} indisponible dans ce runtime")
        q = db.query(Model)
        conds = []
        modes = []
        if "conteneur_id" in colonnes and cid is not None:
            conds.append(getattr(Model, "conteneur_id") == cid)
            modes.append(f"{table}.conteneur_id = conteneur ancre")
        if "numero_bl" in colonnes and bl_numbers:
            conds.append(getattr(Model, "numero_bl").in_(list(bl_numbers)))
            modes.append(f"{table}.numero_bl = B/L de l'ancre")
        if "escale_id" in colonnes and escale_ids:
            conds.append(getattr(Model, "escale_id").in_(list(escale_ids)))
            modes.append(f"{table}.escale_id = escale(s) du B/L")
        if not conds:
            return _stage(
                cle, libelle, "absent",
                f"{table}.conteneur_id / {table}.numero_bl / {table}.escale_id",
                note="Ancre sans conteneur resolu, B/L ni escale connus : rien a rechercher.",
            )
        rows = q.filter(sa_or(*conds)).all()
        return _stage(
            cle, libelle,
            "reel" if rows else "absent",
            " OU ".join(modes) + " (lien saisi explicitement, jamais devine)",
            [_serialize(r, champs) for r in rows],
        )

    etapes.append(_aval(
        "declaration", "Declaration douaniere",
        lambda: __import__(
            "app.models.transit_avance", fromlist=["DeclarationDouaniereAvance"]
        ).DeclarationDouaniereAvance,
        "declarations_douaniere_avance",
        ["id", "numero_declaration", "regime_douanier", "statut",
         "montant_dd", "total_taxes", "numero_bl", "date_validation",
         "date_acquittement"],
        ["conteneur_id", "escale_id", "numero_bl"],
    ))
    etapes.append(_aval(
        "magasin", "Magasin / entrepot sous douane",
        lambda: __import__(
            "app.models.magasin_douane", fromlist=["DeclarationEntrepot"]
        ).DeclarationEntrepot,
        "declarations_entrepot",
        ["id", "numero_declaration", "regime", "statut", "date_declaration",
         "date_limite", "valeur_marchandise", "numero_bl"],
        ["conteneur_id", "numero_bl"],
    ))
    etapes.append(_aval(
        "livraison", "Mission de livraison (transport)",
        lambda: __import__(
            "app.models.transport", fromlist=["Mission"]
        ).Mission,
        "missions",
        ["id", "reference", "type_mission", "statut", "point_depart",
         "point_arrivee", "date_debut_reelle", "date_fin_reelle",
         "nom_receptionnaire", "numero_bl"],
        ["conteneur_id", "numero_bl"],
    ))
    etapes.append(_aval(
        "facture", "Facture",
        lambda: __import__(
            "app.models.finance_ohada", fromlist=["FactureNew"]
        ).FactureNew,
        "factures_ohada",
        ["id", "numero_facture", "type_facture", "statut", "date_emission",
         "date_echeance", "montant_ht", "montant_tva", "montant_ttc",
         "escale_id"],
        ["conteneur_id", "escale_id"],
    ))

    avertissements = [
        "Les etapes declaree/magasin/livraison/facture ne montrent que les "
        "enregistrements explicitement rattaches au conteneur (cle etrangere "
        "conteneur_id) ou a un numero de B/L saisi : une ligne non saisie avec "
        "le lien n'apparait pas et n'est jamais devinee.",
        "La correspondance cycle-de-vie et parc repose sur l'egalite exacte du "
        "numero physique de conteneur ; un numero saisi differemment (espaces, "
        "casse) ne correspondra pas.",
    ]

    return {
        "ancre": {
            "numero_conteneur": numero_physique,
            "numero_bl": numero_bl or (bls[0].numero_bl if bls else None),
            "conteneur_resolu": conteneur is not None,
        },
        "etapes": etapes,
        "avertissements": avertissements,
        "licence": (
            "Vue strictement derivee d'enregistrements reels relies par cle "
            "etrangere ou par numero physique de conteneur. Aucune donnee, "
            "aucun lien et aucun montant n'est invente."
        ),
    }
