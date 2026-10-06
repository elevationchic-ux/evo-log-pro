"""Tenant service - Multi-tenant SAAS management for Companies, Subscriptions, B2B Portals"""
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from app.models.tenant import (
    Company, SubscriptionPlan, Subscription, Department, B2BPortal, TenantAuditLog
)
from app.models.user import User


class CompanyService:
    """Company management service"""
    
    @staticmethod
    def creer_company(
        db: Session,
        code: str,
        nom: str,
        legal_form: str,
        tax_id: str,
        email: str,
        telephone: str,
        subscription_plan_id: int,
        created_by: int
    ) -> Company:
        """Create a new company/tenant"""
        # Generate subdomain
        subdomain = f"{code.lower()}.evolog.cm"
        
        company = Company(
            code=code,
            nom=nom,
            legal_form=legal_form,
            tax_id=tax_id,
            email=email,
            telephone=telephone,
            subscription_plan_id=subscription_plan_id,
            subscription_start=date.today(),
            subscription_end=date.today() + timedelta(days=30),  # 30 days trial
            subdomain=subdomain,
            is_active=True,
            is_verified=False,
            created_by=created_by
        )
        db.add(company)
        db.commit()
        db.refresh(company)
        
        # Create default B2B portal
        B2BPortalService.creer_b2b_portal(db, company.id)
        
        # Log audit
        TenantAuditLogService.log_action(
            db, company_id=company.id, user_id=created_by,
            action="create_company", entity_type="company", entity_id=company.id
        )
        
        return company
    
    @staticmethod
    def activer_company(db: Session, company_id: int) -> Company:
        """Activate a company"""
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            raise ValueError("Company non trouvée")
        
        company.is_active = True
        company.is_verified = True
        company.verification_date = datetime.utcnow()
        db.commit()
        db.refresh(company)
        return company
    
    @staticmethod
    def suspendre_company(db: Session, company_id: int, raison: str) -> Company:
        """Suspend a company"""
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            raise ValueError("Company non trouvée")
        
        company.is_active = False
        db.commit()
        db.refresh(company)
        return company
    
    @staticmethod
    def mettre_a_jour_quota(db: Session, company_id: int, max_users: int, max_storage_mb: int) -> Company:
        """Update company quotas"""
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            raise ValueError("Company non trouvée")
        
        company.max_users = max_users
        company.max_storage_mb = max_storage_mb
        db.commit()
        db.refresh(company)
        return company


class SubscriptionPlanService:
    """Subscription plan management service"""
    
    @staticmethod
    def creer_plan(
        db: Session,
        code: str,
        nom: str,
        type_plan: str,
        prix_mensuel: float,
        prix_annuel: float,
        max_users: int,
        max_storage_mb: int
    ) -> SubscriptionPlan:
        """Create a subscription plan"""
        plan = SubscriptionPlan(
            code=code,
            nom=nom,
            type_plan=type_plan,
            prix_mensuel=prix_mensuel,
            prix_annuel=prix_annuel,
            max_users=max_users,
            max_storage_mb=max_storage_mb,
            is_active=True
        )
        db.add(plan)
        db.commit()
        db.refresh(plan)
        return plan


class SubscriptionService:
    """Subscription management service"""
    
    @staticmethod
    def creer_subscription(
        db: Session,
        company_id: int,
        plan_id: int,
        start_date: date,
        end_date: date,
        amount: float
    ) -> Subscription:
        """Create a subscription"""
        subscription = Subscription(
            company_id=company_id,
            plan_id=plan_id,
            start_date=start_date,
            end_date=end_date,
            amount=amount,
            status="active"
        )
        db.add(subscription)
        db.commit()
        db.refresh(subscription)
        return subscription
    
    @staticmethod
    def renouveler_subscription(db: Session, subscription_id: int) -> Subscription:
        """Renew a subscription"""
        subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
        if not subscription:
            raise ValueError("Subscription non trouvée")
        
        # Extend by 1 year
        new_end_date = subscription.end_date + timedelta(days=365)
        subscription.end_date = new_end_date
        subscription.status = "active"
        db.commit()
        db.refresh(subscription)
        return subscription


class DepartmentService:
    """Department management service"""
    
    @staticmethod
    def creer_department(
        db: Session,
        company_id: int,
        code: str,
        nom: str,
        description: str,
        manager_id: int
    ) -> Department:
        """Create a department"""
        department = Department(
            company_id=company_id,
            code=code,
            nom=nom,
            description=description,
            manager_id=manager_id,
            is_active=True
        )
        db.add(department)
        db.commit()
        db.refresh(department)
        return department


class B2BPortalService:
    """B2B Portal management service"""
    
    @staticmethod
    def creer_b2b_portal(db: Session, company_id: int) -> B2BPortal:
        """Create B2B portal for a company"""
        portal = B2BPortal(
            company_id=company_id,
            primary_color="#3B82F6",
            secondary_color="#10B981",
            enable_chat=True,
            enable_quotes=True,
            enable_tracking=True,
            enable_api=False,
            is_active=True
        )
        db.add(portal)
        db.commit()
        db.refresh(portal)
        return portal
    
    @staticmethod
    def personnaliser_portal(
        db: Session,
        portal_id: int,
        primary_color: str,
        secondary_color: str,
        logo_url: str
    ) -> B2BPortal:
        """Customize B2B portal"""
        portal = db.query(B2BPortal).filter(B2BPortal.id == portal_id).first()
        if not portal:
            raise ValueError("Portal non trouvé")
        
        portal.primary_color = primary_color
        portal.secondary_color = secondary_color
        portal.logo_url = logo_url
        db.commit()
        db.refresh(portal)
        return portal


class TenantAuditLogService:
    """Tenant audit log service"""
    
    @staticmethod
    def log_action(
        db: Session,
        company_id: int,
        user_id: int,
        action: str,
        entity_type: str,
        entity_id: int,
        old_values: dict = None,
        new_values: dict = None
    ) -> TenantAuditLog:
        """Log a tenant-level action"""
        import json
        
        log = TenantAuditLog(
            company_id=company_id,
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            old_values=json.dumps(old_values) if old_values else None,
            new_values=json.dumps(new_values) if new_values else None
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return log


class TenantReportingService:
    """Tenant reporting service"""
    
    @staticmethod
    def rapport_companies(db: Session) -> Dict[str, Any]:
        """Rapport entreprises : comptes SQL réels, aucune valeur inventée.

        Correction : l'ancienne version écrivait
        `{c.subscription_plan.code: 1 for c in companies}` — une répartition
        factice où chaque plan affichait « 1 » quelle que soit la volumétrie
        (5 entreprises sur un plan n'étaient comptées qu'une fois, la dernière
        écrasant les autres). Ici on compte réellement par plan (jointure +
        GROUP BY), et les totaux viennent de COUNT SQL, pas de la liste en
        mémoire."""
        total = db.query(func.count(Company.id)).scalar() or 0
        actives = db.query(func.count(Company.id)).filter(Company.is_active == True).scalar() or 0
        trial = db.query(func.count(Company.id)).filter(Company.is_verified == False).scalar() or 0
        par_plan_rows = (
            db.query(SubscriptionPlan.code, func.count(Company.id))
            .join(Company, Company.subscription_plan_id == SubscriptionPlan.id)
            .group_by(SubscriptionPlan.code)
            .all()
        )
        par_plan = {code: int(n) for code, n in par_plan_rows}

        return {
            "total_companies": total,
            "actives": actives,
            "trial": trial,
            "par_plan": par_plan,
        }

    @staticmethod
    def rapport_revenus(db: Session, periode: str) -> Dict[str, Any]:
        """Rapport revenus : somme et répartitions calculées en base.

        `par_statut` était écrit `{s.status: 1 ...}` (un par statut, factice).
        On compte maintenant les abonnements réellement groupés par statut, et
        le revenu total est une somme SQL (coalesce à 0 si aucune ligne)."""
        total = db.query(func.count(Subscription.id)).scalar() or 0
        revenu_total = float(db.query(func.coalesce(func.sum(Subscription.amount), 0)).scalar() or 0)
        par_statut_rows = (
            db.query(Subscription.status, func.count(Subscription.id))
            .group_by(Subscription.status)
            .all()
        )
        # `status` est une colonne Enum sans values_callable : la base stocke le
        # NOM ; on restitue la valeur (ex. 'active') telle que sérialisée par l'API.
        par_statut = {
            (s.value if hasattr(s, "value") else str(s)): int(n)
            for s, n in par_statut_rows
        }

        return {
            "periode": periode,
            "total_subscriptions": total,
            "revenu_total": revenu_total,
            "par_statut": par_statut,
        }
