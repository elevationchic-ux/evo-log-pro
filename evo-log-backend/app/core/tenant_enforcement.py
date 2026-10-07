"""
Centralized tenant-isolation enforcement at the ORM layer.

Instead of touching 60+ routers, every SELECT/UPDATE/DELETE issued through an
ORM Session is rewritten here when a tenant context is active:

- SELECT  : adds ``WHERE <table>.company_id = :current_tenant`` for every
            mapped entity that owns a ``company_id`` column (via
            ``with_loader_criteria``, which also covers relationship/lazy loads).
- UPDATE /
  DELETE  : same predicate appended to the statement (ORM-enabled DML).
- INSERT  : ``before_flush`` stamps new rows with the current tenant when the
            model has ``company_id`` and the router left it unset.

Safety properties
-----------------
* Fails OPEN when no tenant context is set (workers, login, migrations,
  seeders) and honours ``bypass_tenant_filter()`` for legit cross-tenant
  super-admin operations.
* Models without a ``company_id`` column are untouched (global master data
  such as ports, incoterms, plan_comptable...).
* The set of tenant-scoped mappers is computed lazily once, after models are
  imported, and cached.
"""
import logging

from sqlalchemy import event, inspect as sa_inspect
from sqlalchemy.orm import Session, with_loader_criteria

from app.core.tenant_context import (
    get_current_tenant,
    is_enforcement_active,
)

logger = logging.getLogger(__name__)

# Cached lazily: list of (mapped_class) with a local company_id column, plus the
# size of the mapper registry observed when that list was computed. Some ORM
# entities bearing company_id are declared in modules pulled in only by the
# routers (app.main), not by app.models.__init__ (ex. Navire/Escale via
# acconage, BonCommande via acquisition, BonReception via magasin_avance,
# OrdreTransport via transport_international, DeclarationFiscale/ContratFiscal/
# RetenueSourceCameroun via fiscalite_cameroun). If the very first tenant query
# runs while the registry is still partial, a permanently-cached list would
# freeze an INCOMPLETE set and silently leave those tables unscoped (cross-
# tenant leak). The list is therefore re-synced whenever the registry grew, so
# the tracked set always equals the live enumeration (the invariant asserted by
# tests/unit/test_tenant_http_isolation.py). In production the registry is
# stable after startup, so this is a cheap len() check per query.
_tenant_classes: list | None = None
_tenant_registry_size: int = -1


def _tenant_scoped_classes() -> list:
    global _tenant_classes, _tenant_registry_size
    from app.core.database import Base
    registry_size = len(list(Base.registry.mappers))
    if _tenant_classes is None or registry_size != _tenant_registry_size:
        import app.models  # noqa: F401 - ensures base mapper registration
        classes = []
        for mapper in Base.registry.mappers:
            # mapper.columns inclut les colonnes HERITEES (herite de table Jointe
            # ex. Client -> Tiers.company_id). On filtre donc aussi les sous-
            # classes qui ne portent pas la colonne dans leur propre table.
            if "company_id" in mapper.columns:
                classes.append(mapper.class_)
        _tenant_classes = classes
        _tenant_registry_size = registry_size
        logger.info(
            "Tenant enforcement: %d tenant-scoped entities (company_id) tracked",
            len(classes),
        )
    return _tenant_classes


def reset_tenant_class_cache() -> None:
    """Test hook: force re-computation after model changes."""
    global _tenant_classes, _tenant_registry_size
    _tenant_classes = None
    _tenant_registry_size = -1


@event.listens_for(Session, "do_orm_execute")
def _apply_tenant_criteria(orm_state):
    if not (orm_state.is_select or orm_state.is_update or orm_state.is_delete):
        return
    if not is_enforcement_active():
        return
    company_id = get_current_tenant()

    if orm_state.is_select:
        # Ne pas re-ecrire les chargements internes (column/relationship loaders).
        if orm_state.is_column_load or orm_state.is_relationship_load:
            return
        cid = company_id  # captured per-statement; the callable receives the class
        options = [
            with_loader_criteria(
                cls,
                lambda cls_: cls_.company_id == cid,
                include_aliases=True,
            )
            for cls in _tenant_scoped_classes()
        ]
        orm_state.statement = orm_state.statement.options(*options)
    else:
        # UPDATE / DELETE: scope by table when the target is tenant-scoped.
        # On compare par NOM (pas par identite): statement.table est une copie
        # annotee/clonnee de la Table, donc `is` echouerait et le filtre ne
        # serait jamais applique (cross-tenant possible).
        statement = orm_state.statement
        table = getattr(statement, "table", None)
        table_name = getattr(table, "name", None)
        if table_name is not None:
            for cls in _tenant_scoped_classes():
                if sa_inspect(cls).local_table.name == table_name:
                    statement = statement.where(cls.company_id == company_id)
                    orm_state.statement = statement
                    break


@event.listens_for(Session, "before_flush")
def _stamp_tenant_on_insert(session, flush_context, instances):
    if not is_enforcement_active():
        return
    company_id = get_current_tenant()
    classes = None  # computed once below if needed
    for obj in session.new:
        state = sa_inspect(obj, raiseerr=False)
        if state is None:
            continue
        mapper = state.mapper
        if "company_id" not in {c.key for c in mapper.column_attrs}:
            continue
        if getattr(obj, "company_id", None) is None:
            if classes is None:
                classes = {cls.__name__ for cls in _tenant_scoped_classes()}
            if obj.__class__.__name__ in classes:
                obj.company_id = company_id
