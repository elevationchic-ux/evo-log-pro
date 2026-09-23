"""
Étanchéité multi-tenant : preuves automatisées que l'application centralisée
(app.core.tenant_enforcement + app.core.tenant_context) isole bien les
sociétés au niveau ORM, sans dépendre de la bonne volonté des routers.

Scénarios couverts :
  1. SELECT filtré par le tenant courant.
  2. Bypass explicite (super-admin / billing) -> voit tout.
  3. Contexte absent (worker / login) -> fail open, voit tout.
  4. INSERT auto-stampé avec le tenant courant quand le router l'omet.
  5. UPDATE/DELETE ne touchent JAMAIS les lignes d'une autre société.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.models  # noqa: F401 - enregistre tous les mappers
import app.main  # noqa: F401 - parite runtime : enregistre AUSSI les modeles
# imports uniquement par les routers (navires/acconage), indispensable a un
# create_all complet.
import app.core.tenant_enforcement  # noqa: F401 - installe les evenements ORM
from app.core.database import Base
from app.core.tenant_context import (
    bypass_tenant_filter,
    clear_current_tenant,
    set_current_tenant,
)
from app.models.tenant import Company, Department
from app.models.tiers import Client, TiersType


@pytest.fixture()
def session():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    # Deux sociétés distinctes
    alpha = Company(nom="Alpha Logistics", code="ALPHA")
    beta = Company(nom="Beta Transport", code="BETA")
    db.add_all([alpha, beta])
    db.commit()
    db._alpha_id, db._beta_id = alpha.id, beta.id
    # Un département par société (créés sans contexte tenant actif)
    db.add(Department(company_id=alpha.id, code="OPS", nom="Exploitation Alpha"))
    db.add(Department(company_id=beta.id, code="OPS", nom="Exploitation Beta"))
    db.commit()
    try:
        yield db
    finally:
        clear_current_tenant()
        db.close()


def _dept_names(db):
    return sorted(d.nom for d in db.query(Department).all())


def test_select_is_scoped_to_current_tenant(session):
    set_current_tenant(session._alpha_id)
    assert _dept_names(session) == ["Exploitation Alpha"]

    set_current_tenant(session._beta_id)
    session.expire_all()
    assert _dept_names(session) == ["Exploitation Beta"]


def test_bypass_sees_everything(session):
    set_current_tenant(session._alpha_id)
    with bypass_tenant_filter():
        session.expire_all()
        assert len(_dept_names(session)) == 2


def test_no_context_fails_open(session):
    clear_current_tenant()
    assert len(_dept_names(session)) == 2


def test_insert_is_auto_stamped(session):
    set_current_tenant(session._beta_id)
    # Le router oublie company_id : le before_flush doit le renseigner.
    dept = Department(code="FIN", nom="Finance Beta")
    session.add(dept)
    session.commit()
    assert dept.company_id == session._beta_id

    clear_current_tenant()
    session.expire_all()
    stored = session.query(Department).filter_by(code="FIN").one()
    assert stored.company_id == session._beta_id


def test_update_cannot_cross_tenant(session):
    set_current_tenant(session._alpha_id)
    # Evenement bulk-safe : l'UPDATE est re-filtere cote SQL.
    updated = (
        session.query(Department)
        .filter(Department.code == "OPS")
        .update({Department.description: "MADE_IN_ALPHA"}, synchronize_session=False)
    )
    session.commit()
    assert updated == 1  # seulement la ligne d'Alpha

    with bypass_tenant_filter():
        session.expire_all()
        beta_dept = session.query(Department).filter_by(company_id=session._beta_id).one()
        assert beta_dept.description is None  # Beta intacte


def test_delete_cannot_cross_tenant(session):
    set_current_tenant(session._alpha_id)
    session.query(Department).filter(Department.code == "OPS").delete(
        synchronize_session=False
    )
    session.commit()

    with bypass_tenant_filter():
        session.expire_all()
        remaining = session.query(Department).all()
        assert [d.nom for d in remaining] == ["Exploitation Beta"]


def test_joined_inheritance_root_is_scoped(session):
    # Client herite de Tiers (joined-table) : company_id porte par la table
    # mere doit quand meme filtrer les requetes sur la sous-classe.
    alpha, beta = session._alpha_id, session._beta_id
    session.add(Client(company_id=alpha, code="CLI-A", type=TiersType.CLIENT, name="Client Alpha"))
    session.add(Client(company_id=beta, code="CLI-B", type=TiersType.CLIENT, name="Client Beta"))
    session.commit()

    set_current_tenant(alpha)
    session.expire_all()
    assert [c.name for c in session.query(Client).all()] == ["Client Alpha"]

    set_current_tenant(beta)
    session.expire_all()
    assert [c.name for c in session.query(Client).all()] == ["Client Beta"]
