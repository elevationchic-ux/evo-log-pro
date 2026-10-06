"""Tests du rapport SaaS (TenantReportingService).

Régression ciblée : `par_plan` et `par_statut` étaient écrits sous forme de
compréhensions `{cle: 1 for ...}` — chaque clé affichait donc « 1 » quelle que
soit la volumétrie (5 entreprises sur un plan = comptées 1 fois). Ils doivent
maintenant compter RÉELLEMENT par clé (GROUP BY SQL). Idem pour les totaux, qui
viennent de COUNT/SUM SQL et non de la liste chargée en mémoire.
"""
from datetime import date

import pytest
from sqlalchemy.orm import Session

from app.models.tenant import (
    Company, SubscriptionPlan, Subscription,
    SubscriptionPlanType, SubscriptionStatus,
)
from app.services.tenant_service import TenantReportingService


def _plan(db: Session, code: str) -> SubscriptionPlan:
    p = SubscriptionPlan(
        code=code, nom=f"Plan {code}", type_plan=SubscriptionPlanType.PRO,
        prix_mensuel=50000, prix_annuel=500000, is_active=True,
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


def _company(db: Session, code: str, plan: SubscriptionPlan, *, active: bool, verified: bool) -> Company:
    c = Company(
        code=code, nom=f"Societe {code}", legal_form="SARL", tax_id=f"NIF-{code}",
        email=f"contact@{code.lower()}.cm", telephone="+23700000000",
        is_active=active, is_verified=verified,
        subscription_plan_id=plan.id,
    )
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


def _sub(db: Session, company: Company, plan: SubscriptionPlan, status: SubscriptionStatus, amount: float) -> Subscription:
    s = Subscription(
        company_id=company.id, plan_id=plan.id, status=status, amount=amount,
        currency="XAF", start_date=date(2026, 1, 1), end_date=date(2026, 12, 31),
    )
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


class TestRapportCompanies:
    def test_vide_tous_compteurs_a_zero(self, db: Session):
        r = TenantReportingService.rapport_companies(db)
        assert r["total_companies"] == 0
        assert r["actives"] == 0
        assert r["trial"] == 0
        assert r["par_plan"] == {}

    def test_par_plan_compte_reellement(self, db: Session):
        """Coeur de la régression : 2 sociétés sur PRO, 1 sur STARTER.

        L'ancien code renvoyait {'PRO': 1, 'STARTER': 1} (toute clé forcée à 1).
        """
        pro = _plan(db, "PRO")
        starter = _plan(db, "STARTER")
        _company(db, "A1", pro, active=True, verified=True)
        _company(db, "A2", pro, active=False, verified=False)
        _company(db, "B1", starter, active=True, verified=False)

        r = TenantReportingService.rapport_companies(db)
        assert r["total_companies"] == 3
        assert r["par_plan"] == {"PRO": 2, "STARTER": 1}
        assert r["actives"] == 2
        # 'trial' = sociétés non vérifiées (is_verified == False)
        assert r["trial"] == 2


class TestRapportRevenus:
    def test_vide_revenus_zero(self, db: Session):
        r = TenantReportingService.rapport_revenus(db, "2026")
        assert r["periode"] == "2026"
        assert r["total_subscriptions"] == 0
        assert r["revenu_total"] == 0.0
        assert r["par_statut"] == {}

    def test_par_statut_et_somme_reels(self, db: Session):
        """2 abonnements actifs (100 + 100) + 1 trial (50).

        L'ancien `par_statut` renvoyait {'active': 1, 'trial': 1} ; la somme
        était calculée en Python sur la liste entière.
        """
        pro = _plan(db, "PRO")
        c1 = _company(db, "C1", pro, active=True, verified=True)
        c2 = _company(db, "C2", pro, active=True, verified=True)
        c3 = _company(db, "C3", pro, active=False, verified=False)
        _sub(db, c1, pro, SubscriptionStatus.ACTIVE, 100.0)
        _sub(db, c2, pro, SubscriptionStatus.ACTIVE, 100.0)
        _sub(db, c3, pro, SubscriptionStatus.TRIAL, 50.0)

        r = TenantReportingService.rapport_revenus(db, "2026")
        assert r["total_subscriptions"] == 3
        assert r["revenu_total"] == pytest.approx(250.0)
        # Clés = VALEURS d'enum ('active', 'trial'), pas les NOMs stockés.
        assert r["par_statut"] == {"active": 2, "trial": 1}
