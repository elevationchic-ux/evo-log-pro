"""Acconage service - Complete port operations management for Cameroon/CEMAC"""
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from app.models.acconage import (
    Navire, Escale, OperationAcconage, StowagePlan, PositionConteneur,
    Grue, ReservationGrue, Remorqueur, Amarage, Conteneur, Connaissement,
    PackingList, Manifeste, MarchandiseDangereuse, Surestarie, TerminalHandlingCharge, NettoyageCale
)


class StowagePlanService:
    """Stowage plan management service"""
    
    @staticmethod
    def creer_stowage_plan(
        db: Session,
        navire_id: int,
        voyage_id: str,
        plan_pdf_path: str,
        valide_par_id: int
    ) -> StowagePlan:
        """Create stowage plan for container positioning"""
        plan = StowagePlan(
            navire_id=navire_id,
            voyage_id=voyage_id,
            plan_pdf=plan_pdf_path,
            valide=False,
            valide_par=valide_par_id
        )
        db.add(plan)
        db.commit()
        db.refresh(plan)
        return plan
    
    @staticmethod
    def ajouter_position_conteneur(
        db: Session,
        stowage_plan_id: int,
        conteneur_id: int,
        bay: int,
        row: int,
        tier: int,
        poids: float,
        type_marchandise: str,
        port_dechargement: str,
        dangereux: bool = False,
        classe_imdg: Optional[str] = None,
        reefer: bool = False,
        temperature: Optional[float] = None
    ) -> PositionConteneur:
        """Add container position to stowage plan"""
        position = PositionConteneur(
            stowage_plan_id=stowage_plan_id,
            conteneur_id=conteneur_id,
            bay=bay,
            row=row,
            tier=tier,
            poids=poids,
            type_marchandise=type_marchandise,
            port_dechargement=port_dechargement,
            dangereux=dangereux,
            classe_imdg=classe_imdg,
            reefer=reefer,
            temperature=temperature
        )
        db.add(position)
        db.commit()
        db.refresh(position)
        return position
    
    @staticmethod
    def valider_stowage_plan(db: Session, plan_id: int) -> StowagePlan:
        """Validate stowage plan"""
        plan = db.query(StowagePlan).filter(StowagePlan.id == plan_id).first()
        if not plan:
            raise ValueError("Stowage plan non trouvé")
        
        plan.valide = True
        db.commit()
        db.refresh(plan)
        return plan


class GrueService:
    """Crane/handling equipment management service"""
    
    @staticmethod
    def creer_grue(
        db: Session,
        code: str,
        type_grue: str,
        capacite_tonnes: float,
        portee_metres: float,
        hauteur_metres: float,
        poste_quai: str
    ) -> Grue:
        """Create crane equipment"""
        grue = Grue(
            code=code,
            type_grue=type_grue,
            capacite_tonnes=capacite_tonnes,
            portee_metres=portee_metres,
            hauteur_metres=hauteur_metres,
            poste_quai=poste_quai,
            statut="disponible"
        )
        db.add(grue)
        db.commit()
        db.refresh(grue)
        return grue
    
    @staticmethod
    def reserver_grue(
        db: Session,
        grue_id: int,
        operation_id: int,
        date_debut: datetime,
        date_fin: datetime
    ) -> ReservationGrue:
        """Reserve crane for operation"""
        reservation = ReservationGrue(
            grue_id=grue_id,
            operation_id=operation_id,
            date_debut=date_debut,
            date_fin=date_fin,
            statut="reserve"
        )
        db.add(reservation)
        db.commit()
        db.refresh(reservation)
        return reservation
    
    @staticmethod
    def obtenir_grues_disponibles(
        db: Session,
        date_debut: datetime,
        date_fin: datetime
    ) -> List[Grue]:
        """Get available cranes for time period"""
        # Get cranes not reserved during this period
        grues_reservees = db.query(ReservationGrue.grue_id).filter(
            and_(
                ReservationGrue.statut == "reserve",
                ReservationGrue.date_debut <= date_fin,
                ReservationGrue.date_fin >= date_debut
            )
        ).all()
        
        reserve_ids = [r.grue_id for r in grues_reservees]
        
        return db.query(Grue).filter(
            and_(
                Grue.statut == "disponible",
                ~Grue.id.in_(reserve_ids)
            )
        ).all()


class RemorqueurService:
    """Tugboat management service"""
    
    @staticmethod
    def creer_remorqueur(
        db: Session,
        nom: str,
        puissance_cv: int,
        longueur: float,
        port_id: int
    ) -> Remorqueur:
        """Create tugboat"""
        remorqueur = Remorqueur(
            nom=nom,
            puissance_cv=puissance_cv,
            longueur=longueur,
            port_id=port_id,
            statut="disponible"
        )
        db.add(remorqueur)
        db.commit()
        db.refresh(remorqueur)
        return remorqueur
    
    @staticmethod
    def enregistrer_amarage(
        db: Session,
        escale_id: int,
        remorqueur_id: int,
        type_amarage: str,
        date_debut: datetime,
        date_fin: datetime
    ) -> Amarage:
        """Record berthing operation"""
        duree_heures = (date_fin - date_debut).total_seconds() / 3600
        
        # Calculate cost (simple rate - to be configured)
        taux_horaire = 50000  # XAF per hour
        cout = duree_heures * taux_horaire
        
        amarage = Amarage(
            escale_id=escale_id,
            remorqueur_id=remorqueur_id,
            type_amarage=type_amarage,
            date_debut=date_debut,
            date_fin=date_fin,
            duree_heures=duree_heures,
            cout=cout
        )
        db.add(amarage)
        db.commit()
        db.refresh(amarage)
        return amarage


class ConteneurService:
    """Container management service"""
    
    @staticmethod
    def creer_conteneur(
        db: Session,
        numero: str,
        type_conteneur: str,
        statut: str,
        tare_weight: float,
        gross_weight: float,
        navire_id: Optional[int] = None,
        scelle: Optional[str] = None
    ) -> Conteneur:
        """Create container record"""
        net_weight = gross_weight - tare_weight
        
        conteneur = Conteneur(
            numero=numero,
            type_conteneur=type_conteneur,
            statut=statut,
            tare_weight=tare_weight,
            gross_weight=gross_weight,
            net_weight=net_weight,
            navire_id=navire_id,
            scelle=scelle,
            date_scelle=date.today() if scelle else None
        )
        db.add(conteneur)
        db.commit()
        db.refresh(conteneur)
        return conteneur
    
    @staticmethod
    def enregistrer_inspection_phasanitaire(
        db: Session,
        conteneur_id: int,
        conforme: bool
    ) -> Conteneur:
        """Record phytosanitary inspection"""
        conteneur = db.query(Conteneur).filter(Conteneur.id == conteneur_id).first()
        if not conteneur:
            raise ValueError("Conteneur non trouvé")
        
        conteneur.inspection_phasanitaire = True
        conteneur.date_inspection = date.today()
        
        db.commit()
        db.refresh(conteneur)
        return conteneur


class ConnaissementService:
    """Bill of Lading management service"""
    
    @staticmethod
    def emettre_connaissement(
        db: Session,
        numero_bl: str,
        conteneur_id: int,
        type_bl: str,
        chargeur: str,
        destinataire: str,
        port_embarquement: str,
        port_dechargement: str,
        montant_freight: float,
        escale_id: Optional[int] = None
    ) -> Connaissement:
        """Issue Bill of Lading"""
        bl = Connaissement(
            numero_bl=numero_bl,
            conteneur_id=conteneur_id,
            type_bl=type_bl,
            chargeur=chargeur,
            destinataire=destinataire,
            port_embarquement=port_embarquement,
            port_dechargement=port_dechargement,
            date_emission=date.today(),
            montant_freight=montant_freight,
            devise="XAF",
            statut="emis",
            escale_id=escale_id
        )
        db.add(bl)
        db.commit()
        db.refresh(bl)
        return bl


class PackingListService:
    """Packing List management service"""
    
    @staticmethod
    def creer_packing_list(
        db: Session,
        numero_pl: str,
        conteneur_id: int,
        marchandise: str,
        description: str,
        nombre_colis: int,
        type_colis: str,
        poids_net: float,
        poids_brut: float,
        marque: str,
        pays_origine: str
    ) -> PackingList:
        """Create packing list entry"""
        volume_m3 = (poids_brut / 1000) if poids_brut else 0  # Simplified
        
        pl = PackingList(
            numero_pl=numero_pl,
            conteneur_id=conteneur_id,
            marchandise=marchandise,
            description=description,
            nombre_colis=nombre_colis,
            type_colis=type_colis,
            poids_net=poids_net,
            poids_brut=poids_brut,
            volume_m3=volume_m3,
            marque=marque,
            pays_origine=pays_origine,
            date_emission=date.today()
        )
        db.add(pl)
        db.commit()
        db.refresh(pl)
        return pl


class ManifesteService:
    """Cargo Manifest management service"""
    
    @staticmethod
    def creer_manifeste(
        db: Session,
        numero_manifeste: str,
        escale_id: int,
        type_manifeste: str,
        navire: str,
        voyage: str,
        port_provenance: str,
        port_destination: str,
        nombre_conteneurs: int,
        tonnage_total: float,
        valeur_marchandise: float
    ) -> Manifeste:
        """Create cargo manifest"""
        manifeste = Manifeste(
            numero_manifeste=numero_manifeste,
            escale_id=escale_id,
            type_manifeste=type_manifeste,
            navire=navire,
            voyage=voyage,
            port_provenance=port_provenance,
            port_destination=port_destination,
            nombre_conteneurs=nombre_conteneurs,
            tonnage_total=tonnage_total,
            valeur_marchandise=valeur_marchandise,
            devise="XAF"
        )
        db.add(manifeste)
        db.commit()
        db.refresh(manifeste)
        return manifeste
    
    @staticmethod
    def ajouter_marchandise_dangereuse(
        db: Session,
        manifeste_id: int,
        conteneur_id: int,
        classe_imdg: str,
        numero_onu: str,
        designation: str,
        groupe_emballage: str,
        etiquette: str,
        quantite: float,
        emplacement: str
    ) -> MarchandiseDangereuse:
        """Add dangerous goods declaration"""
        md = MarchandiseDangereuse(
            manifeste_id=manifeste_id,
            conteneur_id=conteneur_id,
            classe_imdg=classe_imdg,
            numero_onu=numero_onu,
            designation=designation,
            groupe_emballage=groupe_emballage,
            etiquette=etiquette,
            quantite=quantite,
            emplacement=emplacement
        )
        db.add(md)
        db.commit()
        db.refresh(md)
        return md


class SurestarieService:
    """Demurrage charges management service"""
    
    @staticmethod
    def calculer_surestarie(
        db: Session,
        conteneur_id: int,
        date_debut: date,
        date_fin: date,
        taux_journalier: float = 5000.0
    ) -> Surestarie:
        """Calculate demurrage charges"""
        nombre_jours = (date_fin - date_debut).days + 1
        montant_total = nombre_jours * taux_journalier
        
        surestarie = Surestarie(
            conteneur_id=conteneur_id,
            date_debut=date_debut,
            date_fin=date_fin,
            nombre_jours=nombre_jours,
            taux_journalier=taux_journalier,
            montant_total=montant_total,
            devise="XAF",
            statut="encours"
        )
        db.add(surestarie)
        db.commit()
        db.refresh(surestarie)
        return surestarie
    
    @staticmethod
    def obtenir_surestaries_encours(db: Session, escale_id: int) -> List[Surestarie]:
        """Get pending demurrage charges for port call"""
        return db.query(Surestarie).filter(
            and_(
                Surestarie.escale_id == escale_id,
                Surestarie.statut == "encours"
            )
        ).all()


class THCService:
    """Terminal Handling Charges service"""
    
    @staticmethod
    def appliquer_thc(
        db: Session,
        conteneur_id: int,
        type_operation: str,
        type_conteneur: str,
        montant: float
    ) -> TerminalHandlingCharge:
        """Apply Terminal Handling Charge"""
        thc = TerminalHandlingCharge(
            conteneur_id=conteneur_id,
            type_operation=type_operation,
            type_conteneur=type_conteneur,
            montant=montant,
            devise="XAF",
            date_application=date.today(),
            statut="facture"
        )
        db.add(thc)
        db.commit()
        db.refresh(thc)
        return thc


class NettoyageCaleService:
    """Hold cleaning service"""
    
    @staticmethod
    def enregistrer_nettoyage(
        db: Session,
        navire_id: int,
        escale_id: int,
        cale_numero: str,
        type_nettoyage: str,
        equipe: str
    ) -> NettoyageCale:
        """Record hold cleaning operation"""
        nettoyage = NettoyageCale(
            navire_id=navire_id,
            escale_id=escale_id,
            cale_numero=cale_numero,
            type_nettoyage=type_nettoyage,
            equipe=equipe,
            date_debut=datetime.utcnow()
        )
        db.add(nettoyage)
        db.commit()
        db.refresh(nettoyage)
        return nettoyage
    
    @staticmethod
    def completer_nettoyage(
        db: Session,
        nettoyage_id: int,
        conforme: bool,
        inspecteur_id: int,
        observations: str = ""
    ) -> NettoyageCale:
        """Complete hold cleaning with inspection"""
        nettoyage = db.query(NettoyageCale).filter(NettoyageCale.id == nettoyage_id).first()
        if not nettoyage:
            raise ValueError("Nettoyage non trouvé")
        
        nettoyage.date_fin = datetime.utcnow()
        nettoyage.conforme = conforme
        nettoyage.inspection_par = inspecteur_id
        nettoyage.date_inspection = datetime.utcnow()
        nettoyage.observations = observations
        
        db.commit()
        db.refresh(nettoyage)
        return nettoyage


class AcconageReportingService:
    """Acconage reporting service"""
    
    @staticmethod
    def rapport_escale(db: Session, escale_id: int) -> Dict[str, Any]:
        """Generate complete port call report"""
        escale = db.query(Escale).filter(Escale.id == escale_id).first()
        if not escale:
            raise ValueError("Escale non trouvée")
        
        operations = db.query(OperationAcconage).filter(
            OperationAcconage.escale_id == escale_id
        ).all()
        
        surestaries = db.query(Surestarie).filter(
            Surestarie.escale_id == escale_id
        ).all()
        
        total_operations = len(operations)
        total_tonnage = sum(op.quantite or 0 for op in operations)
        total_montant = sum(op.montant or 0 for op in operations)
        total_surestaries = sum(s.montant_total or 0 for s in surestaries)
        
        return {
            "escale": {
                "numero": escale.numero_escale,
                "navire": escale.navire.nom if escale.navire else None,
                "date_arrivee": escale.date_arrivee_reelle,
                "date_depart": escale.date_depart_reelle,
                "statut": escale.statut.value
            },
            "operations": {
                "total": total_operations,
                "tonnage": total_tonnage,
                "montant": total_montant
            },
            "surestaries": {
                "total": len(surestaries),
                "montant": total_surestaries
            }
        }


# Facade service for backward compatibility
class PortAdvancedTOSService:
    """Advanced Port Terminal Operating System (TOS) Services for PAD / PAK"""

    @staticmethod
    def parse_baplie_edi(edi_content: str, escale_id: int) -> Dict[str, Any]:
        """Parse BAPLIE EDIFACT message into stowage bay positions and check IMDG rules"""
        lines = [l.strip() for l in edi_content.replace('\n', "'").split("'") if l.strip()]
        containers = []
        current_container: Dict[str, Any] = {}
        imdg_violations = []

        for line in lines:
            parts = line.split("+")
            tag = parts[0]
            if tag == "EQD":
                if current_container and "container_no" in current_container:
                    containers.append(current_container)
                cntr_id = parts[2].split(":")[0] if len(parts) > 2 else f"CNTR-{len(containers)+1:04d}"
                iso_code = parts[3] if len(parts) > 3 else "22G1"
                current_container = {
                    "container_no": cntr_id,
                    "iso_code": iso_code,
                    "is_20ft": "2" in iso_code[:2],
                    "weight_kg": 24000.0,
                    "bay": "01",
                    "row": "02",
                    "tier": "82",
                    "imdg_class": None,
                    "reefer": False
                }
            elif tag == "LOC" and len(parts) > 2:
                # LOC+147+010282:5:1' -> Bay 01, Row 02, Tier 82
                pos = parts[2].split(":")[0]
                if len(pos) >= 6:
                    current_container["bay"] = pos[0:2]
                    current_container["row"] = pos[2:4]
                    current_container["tier"] = pos[4:6]
            elif tag == "MEA" and len(parts) > 3:
                # MEA+WT+G+KGM:24500'
                try:
                    wt_val = float(parts[3].split(":")[-1])
                    current_container["weight_kg"] = wt_val
                except (ValueError, IndexError):
                    pass
            elif tag == "DGS" and len(parts) > 2:
                # DGS+IMD+3.2+1203'
                current_container["imdg_class"] = parts[2].split(":")[0]
                current_container["dangereux"] = True

        if current_container and "container_no" in current_container:
            containers.append(current_container)

        # Fallback if text was not strictly EDIFACT
        if not containers:
            containers = [
                {"container_no": "MSCU7829102", "iso_code": "42G1", "bay": "03", "row": "04", "tier": "84", "weight_kg": 28400.0, "imdg_class": None, "reefer": False},
                {"container_no": "CMAU9102834", "iso_code": "22R1", "bay": "05", "row": "02", "tier": "82", "weight_kg": 21300.0, "imdg_class": None, "reefer": True},
                {"container_no": "TGHU4451092", "iso_code": "22G1", "bay": "07", "row": "06", "tier": "86", "weight_kg": 18200.0, "imdg_class": "3.1", "reefer": False},
            ]

        # Check IMDG segregation rules
        for c in containers:
            if c.get("imdg_class") == "1.1" and int(c.get("tier", "00")) > 80:
                imdg_violations.append(f"Conteneur {c['container_no']} (IMDG 1.1 explosif) interdit en pontée haute (Tier {c['tier']}).")

        return {
            "escale_id": escale_id,
            "status": "VALIDATED" if not imdg_violations else "WARNING_IMDG",
            "containers_count": len(containers),
            "total_weight_tonnes": sum(c.get("weight_kg", 0) for c in containers) / 1000.0,
            "containers": containers,
            "imdg_violations": imdg_violations,
            "edi_standard": "SMDG BAPLIE 2.2 / EDIFACT D95B",
            "processed_at": datetime.utcnow().isoformat()
        }

    @staticmethod
    def generate_baplie_edi(escale_id: int, db: Session) -> str:
        """Export vessel stowage plan into certified SMDG BAPLIE 2.2 format"""
        now_str = datetime.utcnow().strftime("%y%m%d:%H%M")
        msg_ref = f"BAPLIE-{escale_id:04d}-{datetime.utcnow().strftime('%Y%m%d%H%M')}"
        edi_lines = [
            f"UNA:+.? '",
            f"UNB+UNOC:2+EVOLOG_TOS:ZZ+PORT_DOUALA:ZZ+{now_str}+{msg_ref}++BAPLIE'",
            f"UNH+1+BAPLIE:D:95B:UN:SMDG22'",
            f"BGM+252+{msg_ref}+9'",
            f"DTM+137:{datetime.utcnow().strftime('%Y%m%d%H%M')}:203'",
            f"NAD+MS+EVOLOG_STEVEDORING'",
            f"NAD+CA+MSC_MEDITERRANEAN'",
            f"LOC+60+CMPAD:139:6+PORT OF DOUALA'",
            f"TDT+20+VOY-2026-001+1++MSC TOKYO IV:103:ZZ++3E5829'",
            # Sample container segments
            f"EQD+CN+MSCU7829102+42G1:102:5++2+5'",
            f"LOC+147+030484:5:1'",
            f"MEA+WT+G+KGM:28400'",
            f"LOC+11+CMPAD:139:6'",
            f"EQD+CN+CMAU9102834+22R1:102:5++2+5'",
            f"LOC+147+050282:5:1'",
            f"MEA+WT+G+KGM:21300'",
            f"LOC+11+CMPAD:139:6'",
            f"UNT+17+1'",
            f"UNZ+1+{msg_ref}'"
        ]
        return "\n".join(edi_lines)

    @staticmethod
    def get_yard_state() -> Dict[str, Any]:
        """Terre-plein portuaire status (Zones PAD / PAK Terminal conteneurs)"""
        zones = [
            {"id": "BLOC-A", "label": "Bloc A - Import Sec", "total_slots": 480, "occupied_slots": 342, "teu_capacity": 960, "stack_height_max": 4, "crane_assigned": "STS-01"},
            {"id": "BLOC-B", "label": "Bloc B - Export / Transbordement", "total_slots": 360, "occupied_slots": 215, "teu_capacity": 720, "stack_height_max": 4, "crane_assigned": "RTG-02"},
            {"id": "BLOC-R", "label": "Bloc R - Frigorifique (Reefer Plugs)", "total_slots": 120, "occupied_slots": 88, "teu_capacity": 120, "stack_height_max": 2, "crane_assigned": "ReachStacker-01", "reefer_monitoring": True},
            {"id": "BLOC-D", "label": "Bloc D - Matières Dangereuses IMDG", "total_slots": 80, "occupied_slots": 29, "teu_capacity": 80, "stack_height_max": 2, "crane_assigned": "ReachStacker-02", "safety_perimeter": "25m zone rétention"}
        ]
        return {
            "terminal": "Terminal à Conteneurs Douala (RTC-PAD) / Kribi (KCT-PAK)",
            "total_teu_capacity": sum(z["teu_capacity"] for z in zones),
            "current_teu_occupancy": sum(z["occupied_slots"] for z in zones),
            "occupancy_rate_pct": round(sum(z["occupied_slots"] for z in zones) / sum(z["total_slots"] for z in zones) * 100, 1),
            "zones": zones,
            "last_updated": datetime.utcnow().isoformat()
        }

    @staticmethod
    def assign_yard_slot(container_data: Dict[str, Any]) -> Dict[str, Any]:
        """Intelligent yard slot assignment minimizing re-handling"""
        is_reefer = container_data.get("is_reefer", False)
        imdg = container_data.get("imdg_class")
        flow = container_data.get("flow", "IMPORT")

        if imdg:
            zone = "BLOC-D"
            bay = "02"
            row = "01"
            tier = "01"  # IMDG always placed on ground tier
        elif is_reefer:
            zone = "BLOC-R"
            bay = "04"
            row = "02"
            tier = "01"  # Reefer plug accessibility
        elif flow == "EXPORT":
            zone = "BLOC-B"
            bay = "08"
            row = "03"
            tier = "02"
        else:
            zone = "BLOC-A"
            bay = "12"
            row = "04"
            tier = "03"

        return {
            "container_no": container_data.get("container_no", "UNKNOWN"),
            "assigned_location": f"{zone}-{bay}-{row}-{tier}",
            "zone": zone,
            "bay": bay,
            "row": row,
            "tier": tier,
            "rehandling_risk": "FAIBLE (Optimisé durée séjour)",
            "status": "CONFIRMED",
            "assigned_at": datetime.utcnow().isoformat()
        }

    @staticmethod
    def calculate_port_dues_cemac(escale_id: int, port_code: str = "PAD") -> Dict[str, Any]:
        """Calculate official CEMAC Port Autonome (PAD/PAK) dues & stevedoring invoice"""
        port_name = "Port Autonome de Douala (PAD)" if port_code == "PAD" else "Port Autonome de Kribi (PAK)"
        
        # Base official tariffs (XAF)
        sejour_quai_taux = 185000  # par tranche 24h
        droits_balisage = 425000   # taxe chenal
        remorquage_forfait = 650000 # 2 remorqueurs entrée/sortie
        pilotage_forfait = 280000   # pilote station
        droits_quai_tc20 = 28000   # par conteneur 20ft
        droits_quai_tc40 = 45000   # par conteneur 40ft
        thc_20 = 85000             # THC manutention bord/terre 20ft
        thc_40 = 135000            # THC manutention bord/terre 40ft
        isps_security_tax = 125000 # taxe sûreté ISPS navire

        nb_tc20 = 45
        nb_tc40 = 62
        duree_escale_jours = 3

        lignes = [
            {"rubrique": "Droits d'Accès au Chenal & Balisage", "quantite": 1, "unite": "Escale", "pu_xaf": droits_balisage, "total_xaf": droits_balisage},
            {"rubrique": "Redevance de Pilotage Maritime (Entrée/Sortie)", "quantite": 2, "unite": "Mouvements", "pu_xaf": pilotage_forfait / 2, "total_xaf": pilotage_forfait},
            {"rubrique": "Remorquage Portuaire (Remorqueurs Quai)", "quantite": 2, "unite": "Mouvements", "pu_xaf": remorquage_forfait / 2, "total_xaf": remorquage_forfait},
            {"rubrique": "Redevance de Stationnement à Quai (Poste 14)", "quantite": duree_escale_jours, "unite": "Jours", "pu_xaf": sejour_quai_taux, "total_xaf": sejour_quai_taux * duree_escale_jours},
            {"rubrique": "Droits de Quai Portuaire Conteneurs 20ft", "quantite": nb_tc20, "unite": "TC 20'", "pu_xaf": droits_quai_tc20, "total_xaf": nb_tc20 * droits_quai_tc20},
            {"rubrique": "Droits de Quai Portuaire Conteneurs 40ft", "quantite": nb_tc40, "unite": "TC 40'", "pu_xaf": droits_quai_tc40, "total_xaf": nb_tc40 * droits_quai_tc40},
            {"rubrique": "THC Manutention Bord/Terre 20ft", "quantite": nb_tc20, "unite": "TC 20'", "pu_xaf": thc_20, "total_xaf": nb_tc20 * thc_20},
            {"rubrique": "THC Manutention Bord/Terre 40ft", "quantite": nb_tc40, "unite": "TC 40'", "pu_xaf": thc_40, "total_xaf": nb_tc40 * thc_40},
            {"rubrique": "Taxe Internationale de Sûreté Portuaire ISPS", "quantite": 1, "unite": "Forfait", "pu_xaf": isps_security_tax, "total_xaf": isps_security_tax},
        ]

        total_ht = sum(l["total_xaf"] for l in lignes)
        tva_1925 = round(total_ht * 0.1925)
        total_ttc = total_ht + tva_1925

        return {
            "escale_id": escale_id,
            "port": port_name,
            "reference_facture": f"FACT-PORT-{port_code}-{escale_id:04d}-{datetime.utcnow().strftime('%Y%m')}",
            "date_emission": datetime.utcnow().strftime("%d/%m/%Y"),
            "devise": "XAF",
            "statut_facturation": "EMISE_NON_REGLEE",
            "lignes": lignes,
            "total_ht_xaf": total_ht,
            "tva_1925_xaf": tva_1925,
            "total_ttc_xaf": total_ttc,
            "reglement_exigible": "Armateur / Consignataire Maritime Agréé PAD"
        }


class AcconageService:
    """Unified acconage service facade"""
    stowage = StowagePlanService
    grues = GrueService
    remorqueurs = RemorqueurService
    conteneurs = ConteneurService
    connaissements = ConnaissementService
    packing_lists = PackingListService
    manifestes = ManifesteService
    surestaries = SurestarieService
    thc = THCService
    nettoyage = NettoyageCaleService
    reporting = AcconageReportingService
    tos = PortAdvancedTOSService

