"""Routeur metier : endpoints de lecture pour les services
metier avances (analytique, alertes, conformite). Donnees reelles
uniquement — chaque service refuse honnetement sans donnees."""
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.permissions import require_perm
from app.models.user import User
from app.services.capteur_carburant_service import CapteurCarburantService
from app.services.paie_service import PaieService
from app.services.rentabilite_service import RentabiliteService
from app.services.rentabilite_mission_service import RentabiliteMissionService
from app.services.economie_service import EconomieService
from app.services.qhse_deep_service import QhseDeepService
from app.services.comptabilite_deep_service import ComptabiliteDeepService
from app.services.transport_b_service import TransportBService
from app.services.magasin_b_service import MagasinBService
from app.services.finance_c_service import FinanceCService
from app.services.rh_c_service import RhCService
from app.services.frais_d_service import FraisDService
from app.services.organization_service import OrganizationService
from app.services.dashboard_deep_service import DashboardDeepService
from app.services.transport_deep_service import TransportDeepService
from app.services.fluvial_b_service import FluvialBService
from app.services.annuaire_service import AnnuaireService
from app.services.prestataire_service import PrestataireService
from app.services.qhse_portal_service import QhsePortalService
from app.services.admin_tenant_service import AdminTenantService
from app.services.reports_deep_service import ReportsDeepService
from app.services.compta_c_service import ComptaCService
from app.services.accreditation_service import AccreditationService
from app.services.superadmin_deep_service import SuperadminDeepService
from app.services.chat_service import ChatService
from app.services.pipeline_e_service import PipelineEService
from app.services.commercial_service import CommercialService
from app.services.employe_service import EmployeService
from app.services.support_service import SupportService
from app.services.chauffeur_service import ChauffeurService
from app.services.declarant_service import DeclarantService
from app.services.collaborateur_service import CollaborateurService
from app.services.chef_personnel_service import ChefPersonnelService
from app.services.formation_service import FormationService
from app.services.technicien_service import TechnicienService
from app.services.qhse_b_service import QhseBService
from app.services.parc_service import ParcService
from app.services.coldchain_e_service import Cold2DoorService
from app.services.transit_b_service import TransitBService
from app.services.conteneur_cycle_service import ConteneurCycleService
from app.services.courier_e_service import CourierEService
from app.services.aerien_service import AirFreightService
from app.services.ferroviaire_service import RailFreightService
from app.services.fluvial_service import FluvialFreightService
from app.services.log3pl_b_service import TplCarrierService
from app.services.gap_bridge_service import TarifService
from app.services.pipeline_e_service import PipelineEService
from app.services.transit_deep_service import CustomsValuationService

router = APIRouter(tags=["metier-analytique"], prefix="/metier")


@router.get("/cuves-en-alerte", summary="Cuves carburant sous seuil")
def cuves_en_alerte(
    seuil_pct: float = Query(20.0),
    db: Session = Depends(get_db),
    current: User = Depends(require_perm("transport.carburant.read")),
) -> Dict[str, Any]:
    return CapteurCarburantService.cuves_en_alerte(db, seuil_pct=seuil_pct)


@router.get("/paie/cumuls", summary="Cumuls paie annuels")
def paie_cumuls(
    annee: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current: User = Depends(require_perm("paie.bulletin.read")),
) -> Dict[str, Any]:
    return PaieService.cumuls_annuels(db, annee=annee)


@router.get("/paie/cumuls-progressifs", summary="IRGM progressif cumule par mois")
def paie_progressifs(
    annee: int = Query(...),
    employe_id: int = Query(...),
    db: Session = Depends(get_db),
    current: User = Depends(require_perm("paie.bulletin.read")),
) -> Dict[str, Any]:
    return PaieService.cumuls_progressifs(db, annee=annee, employe_id=employe_id)


@router.get("/paie/bulletin", summary="Bulletin de paie detaille")
def paie_bulletin(
    employe_id: int = Query(...),
    annee: int = Query(...),
    mois: int = Query(...),
    db: Session = Depends(get_db),
    current: User = Depends(require_perm("paie.bulletin.read")),
) -> Dict[str, Any]:
    return PaieService.bulletin(db, employe_id=employe_id, annee=annee, mois=mois)


@router.get("/paie/bulletin/pdf", summary="Bulletin de paie en PDF")
def paie_bulletin_pdf(
    employe_id: int = Query(...),
    annee: int = Query(...),
    mois: int = Query(...),
    db: Session = Depends(get_db),
    current: User = Depends(require_perm("paie.bulletin.read")),
) -> Response:
    pdf = PaieService.bulletin_pdf(db, employe_id=employe_id, annee=annee, mois=mois)
    return Response(content=pdf, media_type="application/pdf",
                    headers={"Content-Disposition":
                             f"attachment; filename=bulletin_{employe_id}_{annee}_{mois:02d}.pdf"})


@router.get("/rentabilite", summary="CA par client et type")
def rentabilite(
    client_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current: User = Depends(require_perm("comptabilite.balance.read")),
) -> Dict[str, Any]:
    return RentabiliteService.par_client(db, client_id=client_id)


@router.get("/rentabilite/missions", summary="Rentabilite par mission")
def rentabilite_missions(
    mission_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current: User = Depends(require_perm("transport.mission.read")),
) -> Dict[str, Any]:
    return RentabiliteMissionService.par_mission(db, mission_id=mission_id)


@router.get("/indicateurs-financiers", summary="Indicateurs par categorie")
def indicateurs(
    categorie: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current: User = Depends(require_perm("comptabilite.balance.read")),
) -> Dict[str, Any]:
    return EconomieService.indicateurs(db, categorie=categorie)


@router.get("/qhse/depassements", summary="Depassements normes environnementales")
def qhse_depassements(
    db: Session = Depends(get_db),
    current: User = Depends(require_perm("qhse.rapport.read")),
) -> Dict[str, Any]:
    return QhseDeepService.depassements(db)


@router.get("/compta/controle-budgetaire", summary="Budgets et depassements")
def controle_budgetaire(
    db: Session = Depends(get_db),
    current: User = Depends(require_perm("comptabilite.budget_control.read")),
) -> Dict[str, Any]:
    return ComptabiliteDeepService.controle_budgetaire(db)


@router.get("/transport/tournees", summary="Tournees par chauffeur")
def transport_tournees(
    chauffeur: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current: User = Depends(require_perm("transport.dispatch.read")),
) -> Dict[str, Any]:
    return TransportBService.tournees(db, chauffeur=chauffeur)


@router.get("/transport/dg-conformite", summary="Conformite marchandises dangereuses")
def transport_dg(
    db: Session = Depends(get_db),
    current: User = Depends(require_perm("transport.dispatch.read")),
) -> Dict[str, Any]:
    return TransportDeepService.conformite_dg(db)


@router.get("/fluvial/navigabilite", summary="Navigabilite par bief")
def fluvial_nav(
    bief: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current: User = Depends(require_perm("transport.mission.read")),
) -> Dict[str, Any]:
    return FluvialBService.navigabilite(db, bief=bief)


@router.get("/magasin/ecarts", summary="Ecarts d'inventaire")
def magasin_ecarts(
    article: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current: User = Depends(require_perm("magasin.inventaire.read")),
) -> Dict[str, Any]:
    return MagasinBService.ecarts_inventaire(db, article=article)


@router.get("/finance/previsions", summary="Positions de tresorerie previsionnelles")
def finance_previsions(
    db: Session = Depends(get_db),
    current: User = Depends(require_perm("tresorerie.mouvement.read")),
) -> Dict[str, Any]:
    return FinanceCService.previsions(db)


@router.get("/finance/affacturage", summary="Avances d'affacturage")
def finance_affacturage(
    db: Session = Depends(get_db),
    current: User = Depends(require_perm("tresorerie.mouvement.read")),
) -> Dict[str, Any]:
    return FinanceCService.affacturage(db)


@router.get("/rh/formation", summary="Plans de formation et realisation")
def rh_formation(
    db: Session = Depends(get_db),
    current: User = Depends(require_perm("rh.employes.read")),
) -> Dict[str, Any]:
    return RhCService.formation(db)


@router.get("/rh/discipline", summary="Sanctions disciplinaires actives")
def rh_discipline(
    db: Session = Depends(get_db),
    current: User = Depends(require_perm("rh.employes.read")),
) -> Dict[str, Any]:
    return RhCService.discipline(db)


@router.get("/frais/rapports", summary="Notes de frais par statut")
def frais_rapports(
    collaborateur: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current: User = Depends(require_perm("rh.employes.read")),
) -> Dict[str, Any]:
    return FraisDService.rapports(db, collaborateur=collaborateur)


@router.get("/frais/avances", summary="Avances de frais a regulariser")
def frais_avances(
    db: Session = Depends(get_db),
    current: User = Depends(require_perm("rh.employes.read")),
) -> Dict[str, Any]:
    return FraisDService.avances(db)


@router.get("/frais/tva-recuperable", summary="TVA recuperable en attente")
def frais_tva(
    db: Session = Depends(get_db),
    current: User = Depends(require_perm("rh.employes.read")),
) -> Dict[str, Any]:
    return FraisDService.tva_recuperable(db)


@router.get("/organisation/abonnements", summary="Sante des abonnements tenant")
def organisation_abonnements(
    db: Session = Depends(get_db),
    current: User = Depends(require_perm("admin.nomenclature.read")),
) -> Dict[str, Any]:
    return OrganizationService.abonnements(db)


@router.get("/dashboard/sante", summary="Sante des modules et alertes")
def dashboard_sante(
    db: Session = Depends(get_db),
    current: User = Depends(require_perm("dashboard.nomenclature.read")),
) -> Dict[str, Any]:
    return {
        "modules": DashboardDeepService.sante_modules(db),
        "alertes": DashboardDeepService.alertes(db),
    }


@router.get("/annuaire/performance", summary="Performance prestataires annuaire")
def annuaire_performance(
    db: Session = Depends(get_db),
    current: User = Depends(require_perm("acconage.dockers.read")),
) -> Dict[str, Any]:
    return AnnuaireService.performance(db)


@router.get("/annuaire/documents-expires", summary="Documents prestataires expires")
def annuaire_docs(
    db: Session = Depends(get_db),
    current: User = Depends(require_perm("acconage.dockers.read")),
) -> Dict[str, Any]:
    return AnnuaireService.documents_expires(db)


@router.get("/prestataires/homologues", summary="Prestataires homologues")
def prestataires_homologues(
    specialite: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current: User = Depends(require_perm("acconage.dockers.read")),
) -> Dict[str, Any]:
    return PrestataireService.homologues(db, specialite=specialite)


@router.get("/qhse/permis", summary="Permis de travail et conformite")
def qhse_permis(
    db: Session = Depends(get_db),
    current: User = Depends(require_perm("qhse.permis.read")),
) -> Dict[str, Any]:
    return QhsePortalService.permis(db)


@router.get("/qhse/formations", summary="Formations QHSE expirees")
def qhse_formations(
    db: Session = Depends(get_db),
    current: User = Depends(require_perm("qhse.formation.read")),
) -> Dict[str, Any]:
    return QhsePortalService.formations(db)


@router.get("/admin/quotas-tenants", summary="Quotas tenants SaaS")
def admin_quotas(
    db: Session = Depends(get_db),
    current: User = Depends(require_perm("admin.nomenclature.read")),
) -> Dict[str, Any]:
    return AdminTenantService.quotas(db)


@router.get("/admin/sauvegardes", summary="Statut des sauvegardes tenants")
def admin_sauvegardes(
    db: Session = Depends(get_db),
    current: User = Depends(require_perm("admin.nomenclature.read")),
) -> Dict[str, Any]:
    return AdminTenantService.sauvegardes(db)


@router.get("/reports/scorecards", summary="Scorecards par pole")
def reports_scorecards(
    periode: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current: User = Depends(require_perm("dashboard.nomenclature.read")),
) -> Dict[str, Any]:
    return ReportsDeepService.scorecards(db, periode=periode)


@router.get("/compta/contre-passations", summary="Ecritures de contre-passation")
def compta_reversals(
    db: Session = Depends(get_db),
    current: User = Depends(require_perm("comptabilite.balance.read")),
) -> Dict[str, Any]:
    return ComptaCService.contre_passations(db)


@router.get("/accreditations", summary="Accreditations expirees et types")
def accreditations(
    db: Session = Depends(get_db),
    current: User = Depends(require_perm("admin.nomenclature.read")),
) -> Dict[str, Any]:
    return AccreditationService.accreditations(db)


@router.get("/superadmin/incidents", summary="Incidents plateforme ouverts")
def superadmin_incidents(
    db: Session = Depends(get_db),
    current: User = Depends(require_perm("admin.nomenclature.read")),
) -> Dict[str, Any]:
    return SuperadminDeepService.incidents(db)


@router.get("/chat/signalements", summary="Signalements de contenu")
def chat_signalements(
    db: Session = Depends(get_db),
    current: User = Depends(require_perm("admin.nomenclature.read")),
) -> Dict[str, Any]:
    return ChatService.signalements(db)


@router.get("/commercial/pipeline", summary="Pipeline commercial et devis expires")
def commercial_pipeline(
    db: Session = Depends(get_db),
    current: User = Depends(require_perm("dashboard.nomenclature.read")),
) -> Dict[str, Any]:
    return {"pipeline": CommercialService.pipeline(db),
            "devis_expires": CommercialService.devis_expires(db)}


@router.get("/rh/conges/{collaborateur}", summary="Solde de conges collaborateur")
def rh_conges(
    collaborateur: str,
    droit_annuel: int = Query(30),
    db: Session = Depends(get_db),
    current: User = Depends(require_perm("conges.demande.read")),
) -> Dict[str, Any]:
    return EmployeService.solde_conges(db, collaborateur=collaborateur,
                                     droit_annuel=droit_annuel)


@router.get("/support/stats", summary="Tickets support par priorite et statut")
def support_stats(
    db: Session = Depends(get_db),
    current: User = Depends(require_perm("dashboard.nomenclature.read")),
) -> Dict[str, Any]:
    return SupportService.stats_tickets(db)


@router.get("/transport/repos-insuffisants", summary="Chauffeurs avec repos insuffisant")
def transport_repos(
    db: Session = Depends(get_db),
    current: User = Depends(require_perm("transport.dispatch.read")),
) -> Dict[str, Any]:
    return ChauffeurService.repos_insuffisants(db)


@router.get("/douane/declarations-attente", summary="Declarations douanieres en attente")
def douane_attente(
    db: Session = Depends(get_db),
    current: User = Depends(require_perm("transit.declaration.read")),
) -> Dict[str, Any]:
    return DeclarantService.declarations_en_attente(db)


@router.get("/collaborateurs/conformite", summary="Conformite qualite collaborateurs")
def collaborateurs_conformite(
    collaborateur: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current: User = Depends(require_perm("rh.employes.read")),
) -> Dict[str, Any]:
    return CollaborateurService.conformite(db, collaborateur=collaborateur)


@router.get("/recrutement/pipeline", summary="Pipeline de recrutement")
def recrutement_pipeline(
    poste: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current: User = Depends(require_perm("rh.employes.read")),
) -> Dict[str, Any]:
    return ChefPersonnelService.pipeline(db, poste=poste)


@router.get("/formation/certifications", summary="Certifications expirees ou a renouveler")
def formation_certs(
    jours_alerte: int = Query(30),
    db: Session = Depends(get_db),
    current: User = Depends(require_perm("rh.employes.read")),
) -> Dict[str, Any]:
    return FormationService.suivi_certifications(db, jours_alerte=jours_alerte)


@router.get("/maintenance/tickets-severite", summary="Tickets de panne par severite")
def maintenance_tickets(
    db: Session = Depends(get_db),
    current: User = Depends(require_perm("maintindustrielle.work_orders.read")),
) -> Dict[str, Any]:
    return TechnicienService.tickets_par_severite(db)


@router.get("/qhse/quasi-accidents", summary="Quasi-accidents par site")
def qhse_quasi(db: Session = Depends(get_db),
              current: User = Depends(require_perm("qhse.accident.read")),
              ) -> Dict[str, Any]:
    return QhseBService.analyse_quasi_accidents(db)


@router.get("/parc/pneus-a-remplacer", summary="Pneus sous le seuil legal")
def parc_pneus(
    db: Session = Depends(get_db),
    current: User = Depends(require_perm("parc.flotte.read")),
) -> Dict[str, Any]:
    return ParcService.pneus_a_remplacer(db)


@router.get("/froid/bilan-chambre", summary="Bilan thermique par chambre froide")
def froid_bilan(
    chambre: str = Query(...),
    db: Session = Depends(get_db),
    current: User = Depends(require_perm("coldchain.transport_legs.read")),
) -> Dict[str, Any]:
    return Cold2DoorService.bilan_chambre(db, chambre=chambre)


@router.get("/transit/conformite", summary="Taux de conformite des inspections")
def transit_conformite(
    db: Session = Depends(get_db),
    current: User = Depends(require_perm("transit.physical_inspection.read")),
) -> Dict[str, Any]:
    return TransitBService.taux_conformite(db)


@router.get("/conteneurs/{cycle_id}/cycle", summary="Analyse du cycle conteneur")
def conteneur_cycle(
    cycle_id: int,
    db: Session = Depends(get_db),
    current: User = Depends(require_perm("acconage.manifeste.read")),
) -> Dict[str, Any]:
    return ConteneurCycleService.analyser_cycle(db, cycle_id=cycle_id)


@router.get("/coursier/performance/{livreur}", summary="Performance livreur coursier")
def coursier_performance(
    livreur: str,
    db: Session = Depends(get_db),
    current: User = Depends(require_perm("transport.dispatch.read")),
) -> Dict[str, Any]:
    return {
        "performance": CourierEService.performance_livreur(db, livreur=livreur),
        "productivite": CourierEService.productivite_livreur(db, livreur=livreur),
    }


@router.post("/fret/aerien", summary="Calcul fret aerien (poids x prix/kg + surcharges)")
def fret_aerien(
    code_tarif: str,
    poids_kg: int,
    db: Session = Depends(get_db),
    current: User = Depends(require_perm("transport.dispatch.read")),
) -> Dict[str, Any]:
    return AirFreightService.calculer_fret(db, code_tarif=code_tarif, poids_kg=poids_kg)


@router.post("/fret/ferroviaire", summary="Calcul fret ferroviaire (T x km x P - remise)")
def fret_ferroviaire(
    code_tarif: str,
    tonnes: float,
    distance_km: float,
    type_marchandise: Optional[str] = None,
    db: Session = Depends(get_db),
    current: User = Depends(require_perm("transport.dispatch.read")),
) -> Dict[str, Any]:
    return RailFreightService.calculer_fret(
        db, code_tarif=code_tarif, tonnes=tonnes,
        distance_km=distance_km, type_marchandise=type_marchandise)


@router.post("/fret/fluvial", summary="Calcul fret batelier par lettre de voiture")
def fret_fluvial(
    waybill_id: int,
    code_tarif: str,
    db: Session = Depends(get_db),
    current: User = Depends(require_perm("transport.mission.read")),
) -> Dict[str, Any]:
    return FluvialFreightService.calculer_fret(
        db, waybill_id=waybill_id, code_tarif=code_tarif)


@router.post("/fret/3pl", summary="Calcul fret transporteur 3PL")
def fret_3pl(
    code_tarif: str,
    poids_kg: int,
    db: Session = Depends(get_db),
    current: User = Depends(require_perm("transport.dispatch.read")),
) -> Dict[str, Any]:
    return TplCarrierService.calculer_fret(
        db, code_tarif=code_tarif, poids_kg=poids_kg)


@router.post("/tarif/calculer", summary="Prix depuis la grille tarifaire (HT + TVA)")
def tarif_calculer(
    code: str,
    quantite: float,
    db: Session = Depends(get_db),
    current: User = Depends(require_perm("comptabilite.balance.read")),
) -> Dict[str, Any]:
    return TarifService.calculer_prix(db, code=code, quantite=quantite)


@router.get("/pipeline/corrosion/{troncon}", summary="Analyse corrosion troncon pipeline")
def pipeline_corrosion(
    troncon: str,
    seuil_min_mm: float = Query(...),
    db: Session = Depends(get_db),
    current: User = Depends(require_perm("transport.carburant.read")),
) -> Dict[str, Any]:
    return PipelineEService.analyse_corrosion(
        db, troncon=troncon, seuil_min_mm=seuil_min_mm)


@router.get("/douane/valorisation/{valuation_id}", summary="Valeur en douane selon Incoterm")
def douane_valorisation(
    valuation_id: int,
    db: Session = Depends(get_db),
    current: User = Depends(require_perm("transit.customs_valuation.read")),
) -> Dict[str, Any]:
    return CustomsValuationService.calculer_valeur(db, valuation_id=valuation_id)
