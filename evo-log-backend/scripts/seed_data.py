"""
Database seeder - Initializes the database with full multi-tenant SAAS enterprise data
Includes:
- Super Admin (SaaS platform governance): supadmin / supadmin123
- Company Admin (LPC SA): admin / admin123
- Full corporate organigramme accounts: chefmagasin, chefcomptable, dirtransport, etc.
- Multi-tenant company 2 (Trans-Cameroon Logistics): admin_tcl / admin123
- Subscription plans, OHADA chart of accounts, trucks, warehouses, stocks, clients
"""
from sqlalchemy.orm import Session
from datetime import datetime, date
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

from app.core.database import engine, SessionLocal, Base
from app.core.security import get_password_hash
from app.models.tenant import Company, SubscriptionPlan, SubscriptionPlanType
from app.models.organization import Organization
from app.models.user import User, Role
from app.models.agency import Agency
from app.models.tiers import Client, Fournisseur, TiersType
from app.models.transport import Camion, Conducteur
from app.models.finance import Compte
from app.models.magasin import Stock, Entrepot
from app.models.chat import EnterpriseChatMessage
from app.models.prestataire import Prestataire, DemandeCotation
from app.models.chef_personnel import PlanningGarde, PointageVacation, DotationEPI
from app.models.rh import Conge, TypeConge, StatutConge


def seed_subscription_plans(db: Session):
    """Create subscription plans for multi-tenant SAAS"""
    plans = [
        {
            "code": "ENTERPRISE",
            "nom": "SaaS Entreprise Portuaire & Multinationale",
            "type_plan": SubscriptionPlanType.ENTERPRISE,
            "description": "Accès intégral aux 82 modules : Opérations Navire, Acconage, SYDONIA+, Télémétrie FuelGuard, GMAO, B2B et BI Executive.",
            "prix_mensuel": 1500000.0,
            "prix_annuel": 15000000.0,
            "max_users": 100,
            "max_storage_mb": 51200,
            "max_apis_per_day": 50000,
            "modules_inclus": "all,super-admin,admin-tenant,admin-saas,transport,finance,magasin,parc,acconage,qhse,transit,maintenance,cotations,tracking,fuel-guard,procurement,compliance,bi,master-data,rh,client-portal"
        },
        {
            "code": "PRO",
            "nom": "SaaS Professionnel Flotte & Transit",
            "type_plan": SubscriptionPlanType.PRO,
            "description": "Idéal pour transporteurs et transitaires moyens (Gestion flotte, WMS, Comptabilité OHADA et Douane).",
            "prix_mensuel": 650000.0,
            "prix_annuel": 6500000.0,
            "max_users": 25,
            "max_storage_mb": 15360,
            "max_apis_per_day": 15000,
            "modules_inclus": "transport,finance,magasin,parc,transit,compliance,master-data,rh,dashboard"
        },
        {
            "code": "STARTER",
            "nom": "SaaS PME Starter Logistique",
            "type_plan": SubscriptionPlanType.STARTER,
            "description": "Pack de démarrage pour petites entreprises de transport routier et magasins locaux.",
            "prix_mensuel": 250000.0,
            "prix_annuel": 2500000.0,
            "max_users": 5,
            "max_storage_mb": 5120,
            "max_apis_per_day": 5000,
            "modules_inclus": "transport,magasin,finance,dashboard"
        }
    ]

    for p in plans:
        existing = db.query(SubscriptionPlan).filter(SubscriptionPlan.code == p["code"]).first()
        if not existing:
            db.add(SubscriptionPlan(**p))
    db.commit()
    print("✓ Subscription plans seeded (Enterprise, Pro, Starter)")


def seed_companies(db: Session):
    """Seed multi-tenant companies"""
    plan_ent = db.query(SubscriptionPlan).filter(SubscriptionPlan.code == "ENTERPRISE").first()
    plan_pro = db.query(SubscriptionPlan).filter(SubscriptionPlan.code == "PRO").first()

    companies = [
        {
            "code": "LPC",
            "nom": "Logistique Portuaire Cameroun SA",
            "legal_form": "Société Anonyme (SA)",
            "tax_id": "M051800023412P",
            "adresse": "Zone Portuaire Amont, Quai 14, Bonabéri",
            "ville": "Douala",
            "pays": "Cameroun",
            "telephone": "+237 233 42 15 80",
            "email": "contact@lpc-logistics.cm",
            "subscription_plan_id": plan_ent.id if plan_ent else None,
            "subscription_start": date(2026, 1, 1),
            "subscription_end": date(2027, 12, 31),
            "max_users": 100
        },
        {
            "code": "TCL",
            "nom": "Trans-Cameroon Logistics SARL",
            "legal_form": "SARL",
            "tax_id": "M082200045678B",
            "adresse": "Boulevard Maritime, Zone Industrielle Kribi",
            "ville": "Kribi",
            "pays": "Cameroun",
            "telephone": "+237 233 46 88 12",
            "email": "direction@tcl-cameroun.cm",
            "subscription_plan_id": plan_pro.id if plan_pro else None,
            "subscription_start": date(2026, 3, 1),
            "subscription_end": date(2027, 3, 1),
            "max_users": 25
        }
    ]

    for c in companies:
        existing = db.query(Company).filter(Company.code == c["code"]).first()
        if not existing:
            db.add(Company(**c))
    db.commit()
    print("✓ Companies seeded (LPC SA - Douala & TCL SARL - Kribi)")


def seed_organizations(db: Session):
    """Seed organizations for multi-tenant isolation"""
    orgs = [
        {"code": "LPC", "name": "Logistique Portuaire Cameroun SA", "slug": "lpc", "plan": "ENTERPRISE", "status": "ACTIVE"},
        {"code": "TCL", "name": "Trans-Cameroon Logistics SARL", "slug": "tcl", "plan": "BUSINESS", "status": "ACTIVE"},
    ]
    for o in orgs:
        existing = db.query(Organization).filter(Organization.code == o["code"]).first()
        if not existing:
            db.add(Organization(**o))
    db.commit()
    print("✓ Organizations seeded (LPC & TCL)")


def seed_agencies(db: Session):
    """Seed corporate operational agencies"""
    lpc_org = db.query(Organization).filter(Organization.code == "LPC").first()
    tcl_org = db.query(Organization).filter(Organization.code == "TCL").first()

    agencies = [
        Agency(code="HQ", name="Siège Douala Port", city="Douala", is_headquarters=True, organization_id=lpc_org.id if lpc_org else None),
        Agency(code="KRI", name="Agence Port Kribi", city="Kribi", is_headquarters=False, organization_id=lpc_org.id if lpc_org else None),
        Agency(code="BAO", name="Agence Bafoussam Ouest", city="Bafoussam", is_headquarters=False, organization_id=lpc_org.id if lpc_org else None),
        Agency(code="TCL-HQ", name="Siège TCL Kribi", city="Kribi", is_headquarters=True, organization_id=tcl_org.id if tcl_org else None),
        Agency(code="TCL-DLA", name="Bureau Liaison Douala", city="Douala", is_headquarters=False, organization_id=tcl_org.id if tcl_org else None),
    ]

    for agency in agencies:
        if not db.query(Agency).filter(Agency.code == agency.code).first():
            db.add(agency)
    db.commit()
    print("✓ Agencies seeded (Douala HQ, Kribi, Bafoussam, Kribi TCL)")


def seed_roles(db: Session):
    """Seed comprehensive hierarchy of corporate roles"""
    roles_data = [
        {
            "name": "SUPER_ADMIN",
            "description": "Super Administrateur Plateforme SaaS CADC - Gestion des entreprises, abonnements et infrastructure",
            "level": 0,
            "is_system": True,
            "modules_allowed": "all,super-admin,admin-saas,admin-tenant,dashboard"
        },
        {
            "name": "ADMIN",
            "description": "Directeur Général / Administrateur de l'Entreprise - Gestion des utilisateurs, agences et paramètres locaux",
            "level": 1,
            "is_system": True,
            "modules_allowed": "all,admin,admin-tenant,dashboard,master-data,rh,settings,reports-bi"
        },
        {
            "name": "CHEF_MAGASIN",
            "description": "Chef du Département Magasin & Stocks - Supervision des entrepôts, réceptions et valorisations",
            "level": 2,
            "modules_allowed": "magasin,magasin-avance,magasin-douane,magasin-stock,reception-mag3,dashboard"
        },
        {
            "name": "MAGASINIER",
            "description": "Magasinier Opérateur - Préparations de commandes, inventaires et mouvements de stock",
            "level": 3,
            "modules_allowed": "magasin,magasin-stock,reception-mag3,dashboard"
        },
        {
            "name": "CHEF_COMPTABLE",
            "description": "Directeur Administratif & Financier / Chef Comptable - Clôtures OHADA, bilans et fiscalité Cameroun",
            "level": 2,
            "modules_allowed": "finance,finance-ohada,comptabilite-ohada,fiscalite-cameroun,auto-invoicing,dashboard,bi"
        },
        {
            "name": "FINANCIER",
            "description": "Comptable & Facturation - Écritures journalières, factures clients et règlements",
            "level": 3,
            "modules_allowed": "finance,auto-invoicing,paiement-local,transactions,dashboard"
        },
        {
            "name": "DIRECTEUR_TRANSPORT",
            "description": "Directeur des Opérations Transport - Stratégie de flotte, rentabilité et gestion des tournées",
            "level": 2,
            "modules_allowed": "transport,transport-avance,transport-flotte,transport-international,gps-tracking,parc,dashboard"
        },
        {
            "name": "DISPATCHER",
            "description": "Dispatcher Flotte & Régulateur - Affectation des camions, suivi temps réel et feuilles de route",
            "level": 3,
            "modules_allowed": "transport,transport-flotte,tracking,goods,dashboard"
        },
        {
            "name": "CHAUFFEUR",
            "description": "Chauffeur Routier - Bons de livraison, e-POD et application mobile",
            "level": 3,
            "modules_allowed": "chauffeur,mobile-chauffeur"
        },
        {
            "name": "DECLARANT_DOUANE",
            "description": "Déclarant en Douane & Transit - Procédures SYDONIA+, régimes suspensifs et Guichet Unique (GUCE)",
            "level": 2,
            "modules_allowed": "transit,transit-avance,transit-douane,real-customs,bill-of-loading,container-lifecycle,dashboard"
        },
        {
            "name": "CHEF_PARC",
            "description": "Chef de Parc & Maintenance GMAO - Maintenance préventive, engins, pièces de rechange et contrôle technique",
            "level": 2,
            "modules_allowed": "parc,parc-vehicules,maintenance,maintenance-gmao,fuel-guard,dashboard"
        },
        {
            "name": "RESPONSABLE_QHSE",
            "description": "Responsable QHSE - Qualité, Hygiène, Sécurité, Environnement et conformité portuaire ISPS",
            "level": 2,
            "modules_allowed": "qhse,qhse-securite,port-incidents,compliance,dashboard"
        },
        {
            "name": "AUDITEUR",
            "description": "Auditeur Interne & Contrôleur de Gestion - Traçabilité des opérations et conformité réglementaire",
            "level": 2,
            "modules_allowed": "audit,reporting,reports,reports-bi,bi,dashboard"
        },
        # Rôles Passifs & Support Administratif / Terrain
        {
            "name": "SECRETAIRE",
            "description": "Secrétariat de Direction & Accueil - Gestion administrative, courriers, notes et accueil",
            "level": 3,
            "modules_allowed": "portail-employe,chat,documents,dashboard"
        },
        {
            "name": "GARDIEN",
            "description": "Agent de Sécurité & Gardiennage - Contrôle d'accès portuaire, registre entrées/sorties et sécurité site",
            "level": 3,
            "modules_allowed": "portail-employe,chat,qhse,dashboard"
        },
        {
            "name": "AGENT_ENTRETIEN",
            "description": "Technicien de Surface & Hygiène - Entretien des locaux, propreté des entrepôts et des bureaux",
            "level": 3,
            "modules_allowed": "portail-employe,chat,dashboard"
        },
        {
            "name": "SUPPORT_IT",
            "description": "Technicien Support IT & Systèmes - Assistance aux postes utilisateurs, réseaux locaux et matériel",
            "level": 3,
            "modules_allowed": "portail-employe,chat,master-data,dashboard"
        },
        {
            "name": "CHEF_PERSONNEL",
            "description": "Chef du Personnel - Supervision N+1 des rôles passifs, plannings de garde 24/7, validation congés et dotations",
            "level": 2,
            "modules_allowed": "chef-personnel,rh,documents,chat,dashboard"
        },
        {
            "name": "ACHATS",
            "description": "Responsable Achats & Approvisionnements - Annuaire des sous-traitants, consultations et cotations logistiques",
            "level": 2,
            "modules_allowed": "annuaire-prestataires,purchase,suppliers,dashboard"
        }
    ]

    for role_data in roles_data:
        existing = db.query(Role).filter(Role.name == role_data["name"]).first()
        if not existing:
            db.add(Role(**role_data))
        else:
            for k, v in role_data.items():
                setattr(existing, k, v)
    db.commit()
    print("✓ 17 Specialized corporate roles seeded (including support & passive staff)")


def seed_users(db: Session):
    """Seed users for all roles across tenants with dedicated logins and passwords"""
    supadmin_pw = get_password_hash("supadmin123")
    default_pw = get_password_hash("admin123")

    lpc = db.query(Company).filter(Company.code == "LPC").first()
    tcl = db.query(Company).filter(Company.code == "TCL").first()
    lpc_org = db.query(Organization).filter(Organization.code == "LPC").first()
    tcl_org = db.query(Organization).filter(Organization.code == "TCL").first()
    agency_hq = db.query(Agency).filter(Agency.code == "HQ").first()
    agency_tcl = db.query(Agency).filter(Agency.code == "TCL-HQ").first()

    users_data = [
        # 1. Super Admin SaaS Platform
        {
            "username": "supadmin",
            "email": "superadmin@evo-log.cm",
            "full_name": "CADC Super Administrateur SaaS",
            "password": supadmin_pw,
            "is_superuser": True,
            "role_level": 0,
            "role": "SUPER_ADMIN",
            "company_id": None,
            "organization_id": None,
            "agency_id": None
        },
        # 2. Company 1 (LPC SA) - Corporate Organigramme
        {
            "username": "admin",
            "email": "admin@evolog.cm",
            "full_name": "Directeur Général (LPC SA)",
            "password": default_pw,
            "is_superuser": False,
            "role_level": 1,
            "role": "ADMIN",
            "company_id": lpc.id if lpc else None,
            "organization_id": lpc_org.id if lpc_org else None,
            "agency_id": agency_hq.id if agency_hq else None
        },
        {
            "username": "chefmagasin",
            "email": "chef.magasin@evolog.cm",
            "full_name": "Chef Département Magasin & Stocks",
            "password": default_pw,
            "role_level": 2,
            "role": "CHEF_MAGASIN",
            "company_id": lpc.id if lpc else None,
            "organization_id": lpc_org.id if lpc_org else None,
            "agency_id": agency_hq.id if agency_hq else None
        },
        {
            "username": "magasinier",
            "email": "magasinier@evolog.cm",
            "full_name": "Jean Dupont (Magasinier)",
            "password": default_pw,
            "role_level": 3,
            "role": "MAGASINIER",
            "company_id": lpc.id if lpc else None,
            "organization_id": lpc_org.id if lpc_org else None,
            "agency_id": agency_hq.id if agency_hq else None
        },
        {
            "username": "chefcomptable",
            "email": "chef.comptable@evolog.cm",
            "full_name": "Directeur Administratif & Financier OHADA",
            "password": default_pw,
            "role_level": 2,
            "role": "CHEF_COMPTABLE",
            "company_id": lpc.id if lpc else None,
            "organization_id": lpc_org.id if lpc_org else None,
            "agency_id": agency_hq.id if agency_hq else None
        },
        {
            "username": "financier",
            "email": "financier@evolog.cm",
            "full_name": "Sophie Mensah (Comptable)",
            "password": default_pw,
            "role_level": 3,
            "role": "FINANCIER",
            "company_id": lpc.id if lpc else None,
            "organization_id": lpc_org.id if lpc_org else None,
            "agency_id": agency_hq.id if agency_hq else None
        },
        {
            "username": "dirtransport",
            "email": "directeur.transport@evolog.cm",
            "full_name": "Directeur des Opérations Transport",
            "password": default_pw,
            "role_level": 2,
            "role": "DIRECTEUR_TRANSPORT",
            "company_id": lpc.id if lpc else None,
            "organization_id": lpc_org.id if lpc_org else None,
            "agency_id": agency_hq.id if agency_hq else None
        },
        {
            "username": "dispatcher",
            "email": "dispatcher@evolog.cm",
            "full_name": "Marie Koulibaly (Dispatch Flotte)",
            "password": default_pw,
            "role_level": 3,
            "role": "DISPATCHER",
            "company_id": lpc.id if lpc else None,
            "organization_id": lpc_org.id if lpc_org else None,
            "agency_id": agency_hq.id if agency_hq else None
        },
        {
            "username": "chauffeur",
            "email": "chauffeur@evolog.cm",
            "full_name": "Pierre Martin (Chauffeur Lourd)",
            "password": default_pw,
            "role_level": 3,
            "role": "CHAUFFEUR",
            "company_id": lpc.id if lpc else None,
            "organization_id": lpc_org.id if lpc_org else None,
            "agency_id": agency_hq.id if agency_hq else None
        },
        {
            "username": "douane",
            "email": "douane@evolog.cm",
            "full_name": "Kofi Annan (Déclarant Douane Agréé)",
            "password": default_pw,
            "role_level": 2,
            "role": "DECLARANT_DOUANE",
            "company_id": lpc.id if lpc else None,
            "organization_id": lpc_org.id if lpc_org else None,
            "agency_id": agency_hq.id if agency_hq else None
        },
        {
            "username": "parc",
            "email": "parc@evolog.cm",
            "full_name": "Amadou Diallo (Chef de Parc GMAO)",
            "password": default_pw,
            "role_level": 2,
            "role": "CHEF_PARC",
            "company_id": lpc.id if lpc else None,
            "organization_id": lpc_org.id if lpc_org else None,
            "agency_id": agency_hq.id if agency_hq else None
        },
        {
            "username": "qhse",
            "email": "qhse@evolog.cm",
            "full_name": "Paul Nguessan (Responsable Sécurité QHSE)",
            "password": default_pw,
            "role_level": 2,
            "role": "RESPONSABLE_QHSE",
            "company_id": lpc.id if lpc else None,
            "organization_id": lpc_org.id if lpc_org else None,
            "agency_id": agency_hq.id if agency_hq else None
        },
        {
            "username": "auditor",
            "email": "auditor@evolog.cm",
            "full_name": "Fatou Bensouda (Auditeur Interne)",
            "password": default_pw,
            "role_level": 2,
            "role": "AUDITEUR",
            "company_id": lpc.id if lpc else None,
            "organization_id": lpc_org.id if lpc_org else None,
            "agency_id": agency_hq.id if agency_hq else None
        },
        # 3. Personnel de Support & Rôles Passifs (LPC SA)
        {
            "username": "secretaire",
            "email": "secretaire@evolog.cm",
            "full_name": "Amina Ngo Bell (Secrétaire de Direction)",
            "password": default_pw,
            "role_level": 3,
            "role": "SECRETAIRE",
            "company_id": lpc.id if lpc else None,
            "organization_id": lpc_org.id if lpc_org else None,
            "agency_id": agency_hq.id if agency_hq else None
        },
        {
            "username": "gardien",
            "email": "gardien@evolog.cm",
            "full_name": "Moussa Bello (Agent de Sécurité & Gardiennage)",
            "password": default_pw,
            "role_level": 3,
            "role": "GARDIEN",
            "company_id": lpc.id if lpc else None,
            "organization_id": lpc_org.id if lpc_org else None,
            "agency_id": agency_hq.id if agency_hq else None
        },
        {
            "username": "entretien",
            "email": "entretien@evolog.cm",
            "full_name": "Mama Jeanne Manga (Technicienne de Surface)",
            "password": default_pw,
            "role_level": 3,
            "role": "AGENT_ENTRETIEN",
            "company_id": lpc.id if lpc else None,
            "organization_id": lpc_org.id if lpc_org else None,
            "agency_id": agency_hq.id if agency_hq else None
        },
        {
            "username": "supportit",
            "email": "supportit@evolog.cm",
            "full_name": "Alain Mbida (Technicien Support IT)",
            "password": default_pw,
            "role_level": 3,
            "role": "SUPPORT_IT",
            "company_id": lpc.id if lpc else None,
            "organization_id": lpc_org.id if lpc_org else None,
            "agency_id": agency_hq.id if agency_hq else None
        },
        {
            "username": "chefpersonnel",
            "email": "chef.personnel@evolog.cm",
            "full_name": "Marcelle Mbarga (Chef du Personnel)",
            "password": default_pw,
            "role_level": 2,
            "role": "CHEF_PERSONNEL",
            "company_id": lpc.id if lpc else None,
            "organization_id": lpc_org.id if lpc_org else None,
            "agency_id": agency_hq.id if agency_hq else None
        },
        {
            "username": "respachats",
            "email": "achats@evolog.cm",
            "full_name": "Alain Fouda (Responsable Achats & Sous-traitance)",
            "password": default_pw,
            "role_level": 2,
            "role": "ACHATS",
            "company_id": lpc.id if lpc else None,
            "organization_id": lpc_org.id if lpc_org else None,
            "agency_id": agency_hq.id if agency_hq else None
        },
        # 4. Company 2 (Trans-Cameroon Logistics SARL - Isolated Tenant)
        {
            "username": "admin_tcl",
            "email": "admin@tcl-cameroun.cm",
            "full_name": "Directeur Général (TCL SARL Kribi)",
            "password": default_pw,
            "role_level": 1,
            "role": "ADMIN",
            "company_id": tcl.id if tcl else None,
            "organization_id": tcl_org.id if tcl_org else None,
            "agency_id": agency_tcl.id if agency_tcl else None
        },
        {
            "username": "magasinier_tcl",
            "email": "magasin@tcl-cameroun.cm",
            "full_name": "Oumarou Sanda (Magasinier TCL)",
            "password": default_pw,
            "role_level": 3,
            "role": "MAGASINIER",
            "company_id": tcl.id if tcl else None,
            "organization_id": tcl_org.id if tcl_org else None,
            "agency_id": agency_tcl.id if agency_tcl else None
        }
    ]

    for user_data in users_data:
        role_name = user_data.pop("role")
        password = user_data.pop("password")
        
        user = db.query(User).filter(User.username == user_data["username"]).first()
        if not user:
            user = User(
                hashed_password=password,
                must_change_password=False,
                **user_data
            )
            db.add(user)
            db.flush()
        else:
            user.hashed_password = password
            for k, v in user_data.items():
                setattr(user, k, v)
            db.flush()
            
        # Assign role
        role = db.query(Role).filter(Role.name == role_name).first()
        if role and role not in user.roles:
            user.roles.append(role)

    db.commit()
    print("✓ Multi-tenant accounts seeded:")
    print("   👑 Super Admin SaaS: supadmin / supadmin123")
    print("   🏢 Company Admin LPC: admin / admin123")
    print("   🏢 Company Admin TCL: admin_tcl / admin123")
    print("   💼 12 Departmental accounts: chefmagasin, chefcomptable, dirtransport, etc.")


def seed_comptes_ohada(db: Session):
    """Create OHADA compliant chart of accounts"""
    comptes_data = [
        {"numero_compte": "101", "nom_compte": "Capital social", "type_compte": "passif"},
        {"numero_compte": "211", "nom_compte": "Terrains portuaires", "type_compte": "actif"},
        {"numero_compte": "241", "nom_compte": "Matériel automobile et camions", "type_compte": "actif"},
        {"numero_compte": "244", "nom_compte": "Matériel et outillage d'acconage", "type_compte": "actif"},
        {"numero_compte": "311", "nom_compte": "Marchandises générales en magasin", "type_compte": "actif"},
        {"numero_compte": "411", "nom_compte": "Clients logistiques & transitaires", "type_compte": "actif"},
        {"numero_compte": "401", "nom_compte": "Fournisseurs de services & carburant", "type_compte": "passif"},
        {"numero_compte": "442", "nom_compte": "État, retenues à la source (IRPP/TVA)", "type_compte": "passif"},
        {"numero_compte": "521", "nom_compte": "Banque BICEC / Société Générale", "type_compte": "actif"},
        {"numero_compte": "571", "nom_compte": "Caisse principale Douala", "type_compte": "actif"},
        {"numero_compte": "601", "nom_compte": "Achats de consommables et carburant", "type_compte": "charge"},
        {"numero_compte": "612", "nom_compte": "Redevances portuaires PAD / PAK", "type_compte": "charge"},
        {"numero_compte": "624", "nom_compte": "Transports de biens & sous-traitance", "type_compte": "charge"},
        {"numero_compte": "661", "nom_compte": "Rémunérations directes du personnel", "type_compte": "charge"},
        {"numero_compte": "701", "nom_compte": "Prestations de transport routier", "type_compte": "produit"},
        {"numero_compte": "706", "nom_compte": "Services d'acconage et manutention", "type_compte": "produit"},
        {"numero_compte": "708", "nom_compte": "Commissions de transit et dédouanement", "type_compte": "produit"},
    ]

    for compte_data in comptes_data:
        if not db.query(Compte).filter(Compte.numero_compte == compte_data["numero_compte"]).first():
            db.add(Compte(**compte_data))
    db.commit()
    print("✓ OHADA accounts seeded (Classes 1 to 7)")


def seed_transport_data(db: Session):
    """Create sample transport fleet and drivers"""
    lpc = db.query(Company).filter(Company.code == "LPC").first()
    tcl = db.query(Company).filter(Company.code == "TCL").first()

    camions = [
        {"immatriculation": "LT-284-AA", "marque": "Mercedes-Benz", "modele": "Actros 3340", "annee": 2023, "capacite_tonnage": 35},
        {"immatriculation": "LT-591-BB", "marque": "Volvo", "modele": "FH16 540", "annee": 2022, "capacite_tonnage": 40},
        {"immatriculation": "LT-812-CC", "marque": "Scania", "modele": "R500 V8", "annee": 2024, "capacite_tonnage": 32},
        {"immatriculation": "KR-104-TA", "marque": "MAN", "modele": "TGX 26.480", "annee": 2021, "capacite_tonnage": 30},
    ]

    for camion_data in camions:
        if not db.query(Camion).filter(Camion.immatriculation == camion_data["immatriculation"]).first():
            db.add(Camion(**camion_data))

    conducteurs = [
        {"nom": "Martin", "prenom": "Pierre", "numero_permis": "CM-2023-001", "telephone": "+237 699 12 34 56"},
        {"nom": "Kouassi", "prenom": "Yao", "numero_permis": "CM-2023-002", "telephone": "+237 699 23 45 67"},
        {"nom": "Diallo", "prenom": "Ibrahim", "numero_permis": "CM-2023-003", "telephone": "+237 699 34 56 78"},
    ]

    for c in conducteurs:
        if not db.query(Conducteur).filter(Conducteur.numero_permis == c["numero_permis"]).first():
            db.add(Conducteur(**c))

    db.commit()
    print("✓ Transport fleet and drivers seeded")


def seed_magasin_data(db: Session):
    """Create warehouses and stock articles"""
    entrepots = [
        {"code": "MAG-DLA-01", "nom": "Magasin Sous-Douane Quai 14", "ville": "Douala", "capacite": 12000},
        {"code": "MAG-KRI-01", "nom": "Terminal Conteneurs Kribi Port", "ville": "Kribi", "capacite": 25000},
        {"code": "MAG-BAO-01", "nom": "Entrepôt Distribution Ouest", "ville": "Bafoussam", "capacite": 6000},
    ]

    for e in entrepots:
        if not db.query(Entrepot).filter(Entrepot.code == e["code"]).first():
            db.add(Entrepot(**e))

    stocks = [
        {"code_article": "ART-CIM-01", "designation": "Ciment Portland 50kg CPJ-35", "categorie": "Construction", "unite_mesure": "sac", "quantite_disponible": 1500, "prix_unitaire": 5800},
        {"code_article": "ART-FER-12", "designation": "Fer à béton Haute Adhérence 12mm", "categorie": "Métallurgie", "unite_mesure": "tonne", "quantite_disponible": 85, "prix_unitaire": 480000},
        {"code_article": "ART-ENG-05", "designation": "Engrais NPK 20-10-10 Cacao", "categorie": "Agro-Industrie", "unite_mesure": "sac", "quantite_disponible": 600, "prix_unitaire": 22000},
    ]

    for s in stocks:
        if not db.query(Stock).filter(Stock.code_article == s["code_article"]).first():
            db.add(Stock(**s))

    db.commit()
    print("✓ Warehouses and stock items seeded")


def seed_tiers_data(db: Session):
    """Create clients and suppliers"""
    clients = [
        {"code": "CLI-DLA-001", "name": "Société Camerounaise de Construction (SCC)", "city": "Douala", "credit_limit": 150000000, "type": TiersType.CLIENT},
        {"code": "CLI-KRI-002", "name": "Kribi Agro-Export SA", "city": "Kribi", "credit_limit": 80000000, "type": TiersType.CLIENT},
        {"code": "CLI-YDE-003", "name": "Groupe Commercial du Centre (GCC)", "city": "Yaoundé", "credit_limit": 50000000, "type": TiersType.CLIENT},
    ]

    for c in clients:
        if not db.query(Client).filter(Client.code == c["code"]).first():
            db.add(Client(**c))

    fournisseurs = [
        {"code": "FOU-DLA-001", "name": "Cimencam SA", "city": "Douala", "type": TiersType.FOURNISSEUR},
        {"code": "FOU-DLA-002", "name": "TotalEnergies Marketing Cameroun", "city": "Douala", "type": TiersType.FOURNISSEUR},
        {"code": "FOU-KRI-003", "name": "Kribi Port Multiple Operators (KPMO)", "city": "Kribi", "type": TiersType.FOURNISSEUR},
    ]

    for f in fournisseurs:
        if not db.query(Fournisseur).filter(Fournisseur.code == f["code"]).first():
            db.add(Fournisseur(**f))

    db.commit()
    print("✓ Clients and suppliers seeded")


def seed_chat_data(db: Session):
    """Seed initial enterprise forum posts and direct messages"""
    lpc = db.query(Company).filter(Company.code == "LPC").first()
    if not lpc:
        return

    admin_u = db.query(User).filter(User.username == "admin").first()
    qhse_u = db.query(User).filter(User.username == "qhse").first()
    sec_u = db.query(User).filter(User.username == "secretaire").first()
    gard_u = db.query(User).filter(User.username == "gardien").first()
    it_u = db.query(User).filter(User.username == "supportit").first()

    # Grand Forum Posts with Official Role Badges
    forum_messages = [
        {
            "company_id": lpc.id,
            "sender_id": admin_u.id if admin_u else 1,
            "recipient_id": None,
            "channel_type": "forum",
            "content": "Bonjour à toute l'équipe LPC SA ! Bienvenue sur notre nouvel ERP logistique portuaire unifié. Utilisez ce forum général pour vos communications officielles et notes de service.",
            "sender_name_snapshot": "Christian Oussi (DG LPC SA)",
            "sender_role_snapshot": "Directeur Général",
            "is_read": True
        },
        {
            "company_id": lpc.id,
            "sender_id": qhse_u.id if qhse_u else 1,
            "recipient_id": None,
            "channel_type": "forum",
            "content": "⚠️ RAPPEL SÉCURITÉ PORTUAIRE ISPS : Le port des EPI (casque, gilet haute visibilité, chaussures de sécurité) est strictement obligatoire dès la porte d'accès Quai 14.",
            "sender_name_snapshot": "Paul Nguessan",
            "sender_role_snapshot": "Responsable Sécurité QHSE",
            "is_read": True
        },
        {
            "company_id": lpc.id,
            "sender_id": sec_u.id if sec_u else 1,
            "recipient_id": None,
            "channel_type": "forum",
            "content": "📋 INFORMATION RH : Les bulletins de paie du mois en cours sont disponibles dans votre Espace Salarié. Pour toute attestation de travail, rapprochez-vous du secrétariat.",
            "sender_name_snapshot": "Amina Ngo Bell",
            "sender_role_snapshot": "Secrétaire de Direction",
            "is_read": True
        },
        {
            "company_id": lpc.id,
            "sender_id": it_u.id if it_u else 1,
            "recipient_id": None,
            "channel_type": "forum",
            "content": "💻 SUPPORT TECHNIQUE : La passerelle SYDONIA+ douane et le module de pesée pont-bascule sont opérationnels à 100%. N'hésitez pas à m'écrire en message direct en cas de blocage poste.",
            "sender_name_snapshot": "Alain Mbida",
            "sender_role_snapshot": "Technicien Support IT",
            "is_read": True
        },
        {
            "company_id": lpc.id,
            "sender_id": gard_u.id if gard_u else 1,
            "recipient_id": None,
            "channel_type": "forum",
            "content": "🛡️ POSTE DE GARDE : 4 camions porte-conteneurs en attente d'embarquement contrôlés et enregistrés au poste nord. Fluidité normale.",
            "sender_name_snapshot": "Moussa Bello",
            "sender_role_snapshot": "Agent de Sécurité & Gardiennage",
            "is_read": True
        }
    ]

    for f_data in forum_messages:
        existing = db.query(EnterpriseChatMessage).filter(
            EnterpriseChatMessage.content == f_data["content"]
        ).first()
        if not existing:
            db.add(EnterpriseChatMessage(**f_data))

    # Direct 1-to-1 Sample Messages (Secrétaire <-> Gardien)
    if sec_u and gard_u:
        direct_messages = [
            {
                "company_id": lpc.id,
                "sender_id": sec_u.id,
                "recipient_id": gard_u.id,
                "channel_type": "direct",
                "content": "Bonjour Moussa, nous attendons une délégation de la DGI à 10h. Merci de les escorter vers la salle de réunion dès leur arrivée.",
                "sender_name_snapshot": "Amina Ngo Bell",
                "sender_role_snapshot": "Secrétaire de Direction",
                "is_read": True
            },
            {
                "company_id": lpc.id,
                "sender_id": gard_u.id,
                "recipient_id": sec_u.id,
                "channel_type": "direct",
                "content": "Bien reçu Madame Amina, le badge visiteur VIP est préparé. Je vous appelle dès qu'ils passent le portail principal.",
                "sender_name_snapshot": "Moussa Bello",
                "sender_role_snapshot": "Agent de Sécurité & Gardiennage",
                "is_read": True
            }
        ]
        for d_data in direct_messages:
            existing = db.query(EnterpriseChatMessage).filter(
                EnterpriseChatMessage.content == d_data["content"]
            ).first()
            if not existing:
                db.add(EnterpriseChatMessage(**d_data))

    db.commit()
    print("✓ Enterprise Forum & Direct Chat data seeded")


def seed_prestataires_data(db: Session):
    """Seed certified subcontractors & providers (Douala, Kribi, Bafoussam)"""
    lpc = db.query(Company).filter(Company.code == "LPC").first()
    if not lpc:
        return

    prestataires = [
        {
            "company_id": lpc.id,
            "code": "PREST-DCH-01",
            "raison_sociale": "Douala Container Handling (DCH) S.A.",
            "sigle": "DCH Logistics",
            "specialite": "MANUTENTION_PORTUAIRE",
            "tax_id": "M010200084512D",
            "rccm": "RC/DLA/2014/B/1842",
            "agrement_portuaire": "PAD-AGR-2024-089 (Port Autonome de Douala)",
            "est_homologue": True,
            "statut_agrement": "VALIDE",
            "ville": "Douala",
            "zone_portuaire": "Zone Amont Quai 14 & Quai Conteneurs",
            "adresse": "Boulevard du Port Bonabéri, Douala",
            "contact_nom": "Emmanuel Ekwalla",
            "contact_telephone": "+237 233 42 77 10",
            "contact_email": "e.ekwalla@dch-cameroun.com",
            "telephone_astreinte_24h": "+237 677 88 99 00",
            "note_globale": 4.9,
            "nb_missions_realisees": 142,
            "taux_ponctualite": 98.5,
            "taux_conformite_qhse": 99.0,
            "devise": "XAF",
            "taux_journalier_indicatif": 450000,
            "conditions_reglement": "Virement 30j fin de mois",
            "observations": "Partenaire stratégique manutention grues portuaires et engins télescopiques reachstackers.",
            "est_actif": True
        },
        {
            "company_id": lpc.id,
            "code": "PREST-KMS-02",
            "raison_sociale": "Kribi Maritime Security & Safety Services",
            "sigle": "KMSS Kribi",
            "specialite": "GARDIENNAGE_ISPS",
            "tax_id": "M031900142981K",
            "rccm": "RC/KRI/2019/B/0411",
            "agrement_portuaire": "PAK-ISPS-2023-014 (Port Autonome de Kribi)",
            "est_homologue": True,
            "statut_agrement": "VALIDE",
            "ville": "Kribi",
            "zone_portuaire": "Port en Eau Profonde de Mboro",
            "adresse": "Base Logistique PAK, Mboro Kribi",
            "contact_nom": "Capitaine Rostand Mvogo",
            "contact_telephone": "+237 233 46 11 22",
            "contact_email": "operations@kmss-maritime.cm",
            "telephone_astreinte_24h": "+237 699 44 55 66",
            "note_globale": 4.8,
            "nb_missions_realisees": 87,
            "taux_ponctualite": 99.2,
            "taux_conformite_qhse": 100.0,
            "devise": "XAF",
            "taux_journalier_indicatif": 280000,
            "conditions_reglement": "Virement 45j",
            "observations": "Certification Code ISPS Niveau 1 & 2. Patrouilles cynophiles et rondes 24/7 terminal.",
            "est_actif": True
        },
        {
            "company_id": lpc.id,
            "code": "PREST-CP-03",
            "raison_sociale": "CleanPro Hygiène & Nettoyage Industriel SARL",
            "sigle": "CleanPro CM",
            "specialite": "NETTOYAGE_INDUSTRIEL",
            "tax_id": "M092100223114C",
            "rccm": "RC/DLA/2021/B/3091",
            "agrement_portuaire": "PAD-ENV-2025-007 (Hygiène & Traitement)",
            "est_homologue": True,
            "statut_agrement": "VALIDE",
            "ville": "Douala",
            "zone_portuaire": "Zone Industrielle Bassa & Quai Magasins",
            "adresse": "Rue des Entrepôts Bassa, Douala",
            "contact_nom": "Clarisse Ndongo",
            "contact_telephone": "+237 233 43 90 44",
            "contact_email": "contact@cleanpro-cameroun.com",
            "telephone_astreinte_24h": "+237 671 22 33 44",
            "note_globale": 4.7,
            "nb_missions_realisees": 210,
            "taux_ponctualite": 96.0,
            "taux_conformite_qhse": 98.5,
            "devise": "XAF",
            "taux_journalier_indicatif": 120000,
            "conditions_reglement": "Virement 30j",
            "observations": "Désinfection entrepôts WMS, nettoyage des cales de navire et gestion des déchets banals.",
            "est_actif": True
        },
        {
            "company_id": lpc.id,
            "code": "PREST-AHL-04",
            "raison_sociale": "Afric Heavy Logistics & Convois CEMAC S.A.",
            "sigle": "AHL Transport",
            "specialite": "TRANSPORT_LOURD",
            "tax_id": "M071700099451A",
            "rccm": "RC/DLA/2017/B/1502",
            "agrement_portuaire": "MINTRANS-CEMAC-T-2022-441",
            "est_homologue": True,
            "statut_agrement": "VALIDE",
            "ville": "Douala",
            "zone_portuaire": "Corridor Douala-N'Djamena & Bangui",
            "adresse": "Boulevard de l'Aviation, Douala",
            "contact_nom": "Hamidou Ousmanou",
            "contact_telephone": "+237 233 40 88 55",
            "contact_email": "flotte@ahl-logistics.cm",
            "telephone_astreinte_24h": "+237 690 12 34 56",
            "note_globale": 4.6,
            "nb_missions_realisees": 94,
            "taux_ponctualite": 94.8,
            "taux_conformite_qhse": 97.0,
            "devise": "XAF",
            "taux_journalier_indicatif": 850000,
            "conditions_reglement": "50% à la commande, 50% déchargement",
            "observations": "Porte-chars 80 tonnes, transport de transformateurs Eneo et conteneurs hors gabarit.",
            "est_actif": True
        },
        {
            "company_id": lpc.id,
            "code": "PREST-CBL-05",
            "raison_sociale": "CamBunkering Maritime & Carburants Portuaires",
            "sigle": "CamBunkering",
            "specialite": "BUNKERING_CARBURANT",
            "tax_id": "M041600078120M",
            "rccm": "RC/DLA/2016/B/0814",
            "agrement_portuaire": "SNH-PAD-HYDRO-2023-018",
            "est_homologue": True,
            "statut_agrement": "VALIDE",
            "ville": "Douala",
            "zone_portuaire": "Poste Pétrolier PAD Duc d'Albe",
            "adresse": "Quai Pétrolier, Zone Portuaire Douala",
            "contact_nom": "Georges Tchuente",
            "contact_telephone": "+237 233 42 30 19",
            "contact_email": "sales@cambunkering.cm",
            "telephone_astreinte_24h": "+237 674 55 66 77",
            "note_globale": 4.9,
            "nb_missions_realisees": 165,
            "taux_ponctualite": 99.5,
            "taux_conformite_qhse": 100.0,
            "devise": "XAF",
            "taux_journalier_indicatif": 1200000,
            "conditions_reglement": "Comptant à la livraison ou traite 15j",
            "observations": "Soutage gasoil marin MGO et lubrifiants Total/Tradex pour navires de ligne et remorqueurs.",
            "est_actif": True
        },
        {
            "company_id": lpc.id,
            "code": "PREST-WO-06",
            "raison_sociale": "Ouest Transit & Logistique Hauts Plateaux",
            "sigle": "OTL Bafoussam",
            "specialite": "DOUANE_TRANSIT",
            "tax_id": "M082000192341O",
            "rccm": "RC/BFM/2020/B/0219",
            "agrement_portuaire": "DGD-GUCE-AGR-2021-312",
            "est_homologue": True,
            "statut_agrement": "VALIDE",
            "ville": "Bafoussam",
            "zone_portuaire": "Hub Régional Ouest & Dépôt Douanier",
            "adresse": "Avenue Principale Marché A, Bafoussam",
            "contact_nom": "Fabrice Kamga",
            "contact_telephone": "+237 233 44 20 18",
            "contact_email": "bafoussam@otl-transit.cm",
            "telephone_astreinte_24h": "+237 696 33 44 55",
            "note_globale": 4.5,
            "nb_missions_realisees": 73,
            "taux_ponctualite": 95.2,
            "taux_conformite_qhse": 96.0,
            "devise": "XAF",
            "taux_journalier_indicatif": 220000,
            "conditions_reglement": "Virement 30j fin de mois",
            "observations": "Dédouanement fret agricole café/cacao et dispatching hinterland.",
            "est_actif": True
        }
    ]

    for p in prestataires:
        existing = db.query(Prestataire).filter(Prestataire.code == p["code"]).first()
        if not existing:
            db.add(Prestataire(**p))

    db.commit()
    print("✓ Certified Subcontractors & B2B Providers seeded (Douala, Kribi, Bafoussam)")


def seed_chef_personnel_data(db: Session):
    """Seed guard schedules, time pointages, PPE dotations and live leave requests"""
    lpc = db.query(Company).filter(Company.code == "LPC").first()
    sec = db.query(User).filter(User.username == "secretaire").first()
    gard = db.query(User).filter(User.username == "gardien").first()
    entr = db.query(User).filter(User.username == "entretien").first()
    it = db.query(User).filter(User.username == "supportit").first()
    chef = db.query(User).filter(User.username == "chefpersonnel").first()
    admin_u = db.query(User).filter(User.username == "admin").first()

    if not lpc or not sec or not gard:
        return

    today = date.today()

    # 1. Plannings de gardes
    plannings = [
        {
            "company_id": lpc.id,
            "employe_id": gard.id,
            "superviseur_id": chef.id if chef else admin_u.id,
            "date_jour": today,
            "quart": "NUIT (19h-07h)",
            "poste_assigne": "Poste de Contrôle Accès Quai 14 & Camions",
            "statut": "CONFIRME",
            "observations": "Ronde renforcée toutes les 2h avec pointeau électronique."
        },
        {
            "company_id": lpc.id,
            "employe_id": sec.id,
            "superviseur_id": chef.id if chef else admin_u.id,
            "date_jour": today,
            "quart": "STANDARD (08h-17h)",
            "poste_assigne": "Accueil Principal Hall Siège & Badges Visiteurs",
            "statut": "CONFIRME",
            "observations": "Permanence téléphonique et gestion courrier DG."
        },
        {
            "company_id": lpc.id,
            "employe_id": entr.id,
            "superviseur_id": chef.id if chef else admin_u.id,
            "date_jour": today,
            "quart": "MATIN (06h-14h)",
            "poste_assigne": "Entrepôt Magasin Central & Blocs Sanitaires Quai",
            "statut": "EN_POSTE",
            "observations": "Nettoyage industriel pré-inspection QHSE."
        },
        {
            "company_id": lpc.id,
            "employe_id": it.id,
            "superviseur_id": chef.id if chef else admin_u.id,
            "date_jour": today,
            "quart": "JOUR (07h-19h)",
            "poste_assigne": "Salle Serveurs & Assistance Postes Quai Portuaire",
            "statut": "CONFIRME",
            "observations": "Astreinte liaison satellite GUCE et scanners WMS."
        }
    ]

    for pl in plannings:
        existing = db.query(PlanningGarde).filter(
            PlanningGarde.employe_id == pl["employe_id"],
            PlanningGarde.date_jour == pl["date_jour"]
        ).first()
        if not existing:
            db.add(PlanningGarde(**pl))

    # 2. Pointages & Vacations
    pointages = [
        {
            "company_id": lpc.id,
            "employe_id": gard.id,
            "valide_par_id": chef.id if chef else admin_u.id,
            "date_pointage": today,
            "heure_arrivee": "18:45",
            "heure_depart": "07:05",
            "heures_effectives": 12.0,
            "droit_panier_nuit": True,
            "montant_panier": 4500.0,
            "est_valide": True,
            "remarques": "Prise de poste ponctuelle. Panier de nuit validé OHADA."
        },
        {
            "company_id": lpc.id,
            "employe_id": entr.id,
            "valide_par_id": chef.id if chef else admin_u.id,
            "date_pointage": today,
            "heure_arrivee": "05:50",
            "heure_depart": "14:00",
            "heures_effectives": 8.0,
            "droit_panier_nuit": False,
            "montant_panier": 0.0,
            "est_valide": True,
            "remarques": "Émargement biométrique conforme."
        }
    ]

    for pt in pointages:
        existing = db.query(PointageVacation).filter(
            PointageVacation.employe_id == pt["employe_id"],
            PointageVacation.date_pointage == pt["date_pointage"]
        ).first()
        if not existing:
            db.add(PointageVacation(**pt))

    # 3. Dotations EPI
    dotations = [
        {
            "company_id": lpc.id,
            "employe_id": gard.id,
            "attribue_par_id": chef.id if chef else admin_u.id,
            "designation": "Gilet Haute Visibilité Fluo Réfléchissant ISPS Portuaire",
            "categorie": "EPI",
            "date_remise": date(2026, 1, 15),
            "date_renouvellement_prevue": date(2026, 7, 15),
            "numero_serie": "ISPS-DLA-G-401",
            "etat": "BON",
            "est_restitue": False,
            "observations": "Dotation sécurité obligatoire zone sous douane."
        },
        {
            "company_id": lpc.id,
            "employe_id": gard.id,
            "attribue_par_id": chef.id if chef else admin_u.id,
            "designation": "Talkie-Walkie VHF Motorola Quai DP-4801",
            "categorie": "COMMUNICATION",
            "date_remise": date(2026, 2, 1),
            "date_renouvellement_prevue": date(2027, 2, 1),
            "numero_serie": "MOT-VHF-88210",
            "etat": "NEUF",
            "est_restitue": False,
            "observations": "Canal 16 veille sécurité et liaison capitainerie."
        },
        {
            "company_id": lpc.id,
            "employe_id": entr.id,
            "attribue_par_id": chef.id if chef else admin_u.id,
            "designation": "Chaussures de Sécurité Coquées S3 Antidérapantes",
            "categorie": "EPI",
            "date_remise": date(2026, 1, 20),
            "date_renouvellement_prevue": date(2026, 12, 20),
            "numero_serie": "RNG-S3-T39-012",
            "etat": "BON",
            "est_restitue": False,
            "observations": "Conforme normes anti-perforation sols mouillés."
        }
    ]

    for dt in dotations:
        existing = db.query(DotationEPI).filter(
            DotationEPI.employe_id == dt["employe_id"],
            DotationEPI.designation == dt["designation"]
        ).first()
        if not existing:
            db.add(DotationEPI(**dt))

    # 4. Demandes de congés initiales pour test N+1
    conges_test = [
        {
            "employe_id": sec.id,
            "type_conge": TypeConge.CONGE_ANNUEL,
            "date_debut": date(2026, 4, 14),
            "date_fin": date(2026, 4, 21),
            "nombre_jours": 8,
            "motif": "Congé annuel de détente premier semestre (reliquat acquis).",
            "statut": StatutConge.EN_ATTENTE
        },
        {
            "employe_id": gard.id,
            "type_conge": TypeConge.CONGE_EXCEPTIONNEL,
            "date_debut": date(2026, 5, 2),
            "date_fin": date(2026, 5, 5),
            "nombre_jours": 4,
            "motif": "Cérémonie familiale traditionnelle à Bafoussam.",
            "statut": StatutConge.EN_ATTENTE
        }
    ]

    for cg in conges_test:
        existing = db.query(Conge).filter(
            Conge.employe_id == cg["employe_id"],
            Conge.motif == cg["motif"]
        ).first()
        if not existing:
            db.add(Conge(**cg))

    db.commit()
    print("✓ Chef du Personnel data seeded (Guard shifts, time pointages, PPE dotations, live leaves)")


def main():
    print("🌱 Starting EVO-LOG SAAS Database Seeding...")
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables verified")

    db = SessionLocal()
    try:
        seed_subscription_plans(db)
        seed_companies(db)
        seed_organizations(db)
        seed_agencies(db)
        seed_roles(db)
        seed_users(db)
        seed_comptes_ohada(db)
        seed_transport_data(db)
        seed_magasin_data(db)
        seed_tiers_data(db)
        seed_chat_data(db)
        seed_prestataires_data(db)
        seed_chef_personnel_data(db)

        print("\n" + "=" * 60)
        print("✅ DATABASE SEEDING COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("🔐 CREDENTIALS SUMMARY:")
        print("   👑 SUPER ADMIN (Plateforme SaaS CADC):")
        print("      Username : supadmin")
        print("      Password : supadmin123")
        print("\n   🏢 COMPANY ADMIN (LPC SA - Douala):")
        print("      Username : admin (ou admin@evolog.cm)")
        print("      Password : admin123")
        print("\n   🏢 COMPANY ADMIN (TCL SARL - Kribi - Tenant 2):")
        print("      Username : admin_tcl")
        print("      Password : admin123")
        print("\n   👥 CORPORATE ORGANIGRAMME ACCOUNTS (Password: admin123):")
        print("      - chefmagasin   : Chef Département Magasin & Stocks")
        print("      - magasinier    : Magasinier Opérateur")
        print("      - chefcomptable : DAF / Chef Comptable OHADA")
        print("      - financier     : Comptable & Facturation")
        print("      - dirtransport  : Directeur Opérations Transport")
        print("      - dispatcher    : Dispatcher Flotte & Tournées")
        print("      - chauffeur     : Chauffeur Routier / e-POD")
        print("      - douane        : Déclarant Douane & SYDONIA+")
        print("      - parc          : Chef de Parc & Maintenance GMAO")
        print("      - qhse          : Responsable Sécurité QHSE")
        print("      - auditor       : Auditeur Interne & Conformité")
        print("      - chefpersonnel : Chef du Personnel (N+1 Rôles Passifs)")
        print("      - respachats    : Responsable Achats & Sous-traitance")
        print("      - secretaire    : Secrétaire de Direction")
        print("      - gardien       : Agent de Sécurité & Gardiennage")
        print("      - entretien     : Technicienne de Surface & Entretien")
        print("      - supportit     : Technicien Support IT")
        print("=" * 60)

    except Exception as e:
        print(f"❌ Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()