"""Tests unitaires du moteur d'autorisation granulaire (RBAC + accréditations).

Couvre les exigences de la spec (Phase 1) :
  * résolution des permissions avec jokers segmentaires ;
  * non-régression : un rôle sans permission granulaire retombe sur modules_allowed ;
  * expiration des accréditations (une accréditation expirée ne compte plus) ;
  * visibilité hiérarchique visible_user_ids (admin / chef / user) ;
  * modules communs (SharedAccess) accessibles à tout utilisateur authentifié ;
  * garde HTTP 401/403 sur le router /api/v1/rbac désormais sécurisé.

Ces tests sont ADDITIFS : ils n'altèrent aucune route ni test existant.
"""
from datetime import date, timedelta

import pytest

from app.core.security import get_current_user, get_password_hash
from app.main import app
from app.models.tenant import Company
from app.models.user import Permission, Role, User
from app.models.accreditation import Accreditation, SharedAccess
from app.core import permissions as perms


def _mk_company(db, code="ACME"):
    c = Company(code=code, nom=f"{code} SA", is_active=True,
               max_users=100, max_storage_mb=1000, current_storage_mb=0,
               modules_actives='["comptabilite","magasin"]')
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


def _mk_user(db, *, username, level, company=None, dept=None, superuser=False):
    u = User(
        username=username, email=f"{username}@example.com",
        hashed_password=get_password_hash("Admin12345"),
        is_active=True, is_superuser=superuser, role_level=level,
        company_id=(company.id if company else None),
        department_id=dept,
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


def _mk_permission(db, code):
    p = Permission(code=code, name=code)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


# ── 1. Wildcard / correspondance de codes ────────────────────────────────────
def test_match_segment_wildcard():
    assert perms._match("comptabilite.*.*", "comptabilite.journal.read")
    assert perms._match("comptabilite.journal.*", "comptabilite.journal.create")
    assert perms._match("*", "nimporte.quoi.que_ce_soit")
    assert not perms._match("comptabilite.journal.read", "comptabilite.journal.create")
    # un joker ne chevauche pas les segments
    assert not perms._match("comptabilite.*", "tresorerie.journal.read")


def test_effective_permissions_union_role_and_accreditation(db):
    company = _mk_company(db)
    user = _mk_user(db, username="comptable", level=3, company=company)
    role = Role(name="COMPTABLE_T", description="t", level=3,
                company_id=company.id, modules_allowed="[]", is_active=True, is_system=True)
    perm = _mk_permission(db, "comptabilite.journal.read")
    role.permissions.append(perm)
    user.roles.append(role)
    db.commit()

    # accréditation valide qui ajoute un code supplémentaire
    acc = Accreditation(
        user_id=user.id, company_id=company.id, libelle="Supplément lettrage",
        type="permission", permission_code="comptabilite.lettrage.modify",
        statut="actif", date_debut=date.today() - timedelta(days=1),
        date_fin=date.today() + timedelta(days=30),
    )
    db.add(acc)
    db.commit()

    codes = perms.load_effective_permissions(user)
    assert "comptabilite.journal.read" in codes
    assert "comptabilite.lettrage.modify" in codes
    assert perms.can(user, "comptabilite.journal.read") is True
    assert perms.can(user, "comptabilite.bilan.approve") is False


# ── 2. Non-régression : fallback modules_allowed quand aucune permission fine ─
def test_fallback_to_modules_allowed_when_no_granular(db):
    company = _mk_company(db)
    user = _mk_user(db, username="legacy", level=3, company=company)
    role = Role(name="LEGACY", description="t", level=3, company_id=company.id,
                modules_allowed='["comptabilite"]', is_active=True, is_system=True)
    user.roles.append(role)
    db.commit()

    assert perms.load_effective_permissions(user) == set()
    # module autorisé historiquement -> accès conservé
    assert perms.can(user, "comptabilite.journal.read") is True
    # module non autorisé -> refus (identique au comportement actuel)
    assert perms.can(user, "transport.mission.read") is False


# ── 3. Bypass niveaux 0/1 ────────────────────────────────────────────────────
def test_admin_levels_bypass_granularity(db):
    company = _mk_company(db)
    admin = _mk_user(db, username="boss", level=1, company=company)
    assert perms.can(admin, "comptabilite.bilan.approve") is True
    assert perms.can(admin, "transport.mission.delete") is True


# ── 4. Expiration des accréditations ─────────────────────────────────────────
def test_expired_accreditation_not_counted(db):
    company = _mk_company(db)
    user = _mk_user(db, username="temp", level=3, company=company)
    role = Role(name="TEMPROLE", description="t", level=3, company_id=company.id,
                modules_allowed="[]", is_active=True, is_system=True)
    p = _mk_permission(db, "comptabilite.journal.read")
    role.permissions.append(p)
    user.roles.append(role)
    expired = Accreditation(
        user_id=user.id, company_id=company.id, libelle="Expirée",
        type="permission", permission_code="comptabilite.bilan.approve",
        statut="actif", date_debut=date.today() - timedelta(days=20),
        date_fin=date.today() - timedelta(days=1),
    )
    revoked = Accreditation(
        user_id=user.id, company_id=company.id, libelle="Révoquée",
        type="permission", permission_code="tresorerie.mouvement.approve",
        statut="revoque", date_debut=date.today() - timedelta(days=1),
        date_fin=date.today() + timedelta(days=10),
    )
    db.add_all([expired, revoked])
    db.commit()

    codes = perms.load_effective_permissions(user)
    assert "comptabilite.bilan.approve" not in codes  # expirée
    assert "tresorerie.mouvement.approve" not in codes  # révoquée
    assert perms.can(user, "comptabilite.journal.read") is True


# ── 5. Visibilité hiérarchique visible_user_ids ──────────────────────────────
def test_visible_user_ids_levels(db):
    company = _mk_company(db)
    sa = _mk_user(db, username="sa", level=0, superuser=True)
    boss = _mk_user(db, username="boss2", level=1, company=company)
    chef = _mk_user(db, username="chef2", level=2, company=company, dept=5)
    emp_a = _mk_user(db, username="empA", level=3, company=company, dept=5)
    emp_b = _mk_user(db, username="empB", level=3, company=company, dept=5)
    emp_elsewhere = _mk_user(db, username="empC", level=3, company=company, dept=9)

    assert perms.visible_user_ids(db, sa) is None      # SuperAdmin : pas de restriction
    assert perms.visible_user_ids(db, boss) is None     # Admin entreprise : tout le tenant
    visible_chef = perms.visible_user_ids(db, chef)
    assert emp_a.id in visible_chef and emp_b.id in visible_chef
    assert emp_elsewhere.id not in visible_chef         # autre département exclu
    assert chef.id in visible_chef
    assert perms.visible_user_ids(db, emp_a) == {emp_a.id}  # user : lui seul


def test_scope_accreditation_restricts_chef(db):
    company = _mk_company(db)
    chef = _mk_user(db, username="chef3", level=2, company=company, dept=5)
    e1 = _mk_user(db, username="e1", level=3, company=company, dept=5)
    e2 = _mk_user(db, username="e2", level=3, company=company, dept=5)
    acc = Accreditation(
        user_id=chef.id, company_id=company.id, libelle="Périmètre restreint",
        type="scope", perimetre_utilisateurs=f"[{e1.id}]",
        statut="actif", date_debut=date.today() - timedelta(days=1),
    )
    db.add(acc)
    db.commit()

    visible = perms.visible_user_ids(db, chef)
    assert e1.id in visible
    assert e2.id not in visible   # hors périmètre de l'accréditation "scope"


# ── 6. Modules communs accessibles à tout utilisateur authentifié ────────────
def test_shared_module_open_to_regular_user(db):
    company = _mk_company(db)
    user = _mk_user(db, username="worker", level=3, company=company)
    role = Role(name="NOGRAN", description="t", level=3, company_id=company.id,
                modules_allowed="[]", is_active=True, is_system=True)
    user.roles.append(role)
    db.commit()

    # "chat" fait partie de DEFAULT_SHARED_MODULES -> ouvert même sans grant
    assert perms.is_shared_module(user, "chat") is True
    assert perms.can(user, "chat.messages.read") is True

    # Une entreprise peut désactiver un module commun
    sa = SharedAccess(company_id=company.id, module_key="chat",
                      autorise_tous_utilisateurs=False)
    db.add(sa)
    db.commit()
    db.refresh(user)
    assert perms.is_shared_module(user, "chat") is False


# ── 7. Garde HTTP : /api/v1/rbac/tenants réservé SuperAdmin (401/403) ─────────
def test_rbac_router_requires_superadmin(client, db):
    company = _mk_company(db)
    chef = _mk_user(db, username="chefhttp", level=2, company=company)

    # anonyme -> 401 (aucune dépendance d'auth retirée)
    app.dependency_overrides.clear()
    assert client.get("/api/v1/rbac/tenants").status_code == 401

    # chef de département (level 2) -> 403 (réservé au SuperAdmin)
    app.dependency_overrides[get_current_user] = lambda: chef
    assert client.get("/api/v1/rbac/tenants").status_code == 403
    app.dependency_overrides.clear()

    # SuperAdmin -> 200
    sa = _mk_user(db, username="sahttp", level=0, superuser=True)
    app.dependency_overrides[get_current_user] = lambda: sa
    assert client.get("/api/v1/rbac/tenants").status_code == 200
    app.dependency_overrides.clear()


def test_permissions_catalog_endpoint_ok_for_admin(client, db):
    company = _mk_company(db)
    admin = _mk_user(db, username="admincat", level=1, company=company)
    app.dependency_overrides[get_current_user] = lambda: admin
    resp = client.get("/api/v1/rbac/permissions/catalog")
    assert resp.status_code == 200
    tree = resp.json()
    assert any(dom["key"] == "finance" for dom in tree)
    app.dependency_overrides.clear()
