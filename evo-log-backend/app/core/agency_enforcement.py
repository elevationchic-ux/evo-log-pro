"""
Centralized agency (succursale) scoping at the ORM layer.

Mirror of ``app.core.tenant_enforcement`` for the agency dimension:

- SELECT  : adds ``WHERE (agency_id = :current OR agency_id IS NULL)`` for
            every mapped entity owning an ``agency_id`` column, via
            ``with_loader_criteria`` (covers relationship/lazy loads).
- UPDATE /
  DELETE  : same predicate appended to ORM-enabled DML.
- INSERT  : ``before_flush`` stamps new rows with the current agency when the
            model has ``agency_id`` and the value was left unset.

Why ``OR agency_id IS NULL``
----------------------------
Rows created before agency scoping (or deliberately company-wide) carry
``agency_id = NULL``. They stay visible to every agency — NULL means
"shared / not attached", never "hidden". New writes made while an agency is
active are stamped automatically, so data progressively becomes agency-owned.

Exclusions
----------
* ``User`` — ``agency_id`` is an assignment (home agency), not business data;
  filtering it would break authentication when the user switches agency.
* ``Agency`` itself has no ``agency_id`` column (no-op anyway).
* Everything else without the column is untouched.

Safety
------
* Fails OPEN when no agency context is set (no agency selected, workers,
  login) and honours ``bypass_agency_filter()`` for the network console
  (agency CRUD, comparatifs, user assignment).
* The scoped-class list is re-synced whenever the mapper registry grows
  (same rationale as tenant enforcement: late-imported models).
"""
import logging

from sqlalchemy import event, inspect as sa_inspect, or_
from sqlalchemy.orm import Session, with_loader_criteria

from app.core.agency_context import (
    get_current_agency,
    is_agency_enforcement_active,
    is_agency_bypass,
)

logger = logging.getLogger(__name__)

# Classes never auto-scoped even if they carry an ``agency_id`` column.
_AGENCY_EXCLUDED = {"User"}

_agency_classes: list | None = None
_agency_registry_size: int = -1


def _agency_scoped_classes() -> list:
    global _agency_classes, _agency_registry_size
    from app.core.database import Base
    registry_size = len(list(Base.registry.mappers))
    if _agency_classes is None or registry_size != _agency_registry_size:
        import app.models  # noqa: F401 - ensure base mapper registration
        classes = []
        for mapper in Base.registry.mappers:
            if "agency_id" not in mapper.columns:
                continue
            if mapper.class_.__name__ in _AGENCY_EXCLUDED:
                continue
            classes.append(mapper.class_)
        _agency_classes = classes
        _agency_registry_size = registry_size
        logger.info(
            "Agency enforcement: %d agency-scoped entities tracked",
            len(classes),
        )
    return _agency_classes


def reset_agency_class_cache() -> None:
    global _agency_classes, _agency_registry_size
    _agency_classes = None
    _agency_registry_size = -1


def _agency_predicate(cls, agency_id):
    """(agency_id == courant) OR (agency_id IS NULL) — NULL = partage."""
    return or_(cls.agency_id == agency_id, cls.agency_id.is_(None))


@event.listens_for(Session, "do_orm_execute")
def _apply_agency_criteria(orm_state):
    if not (orm_state.is_select or orm_state.is_update or orm_state.is_delete):
        return
    if not is_agency_enforcement_active():
        return
    agency_id = get_current_agency()

    if orm_state.is_select:
        if orm_state.is_column_load or orm_state.is_relationship_load:
            return
        aid = agency_id
        options = [
            with_loader_criteria(
                cls,
                lambda cls_, aid=aid: _agency_predicate(cls_, aid),
                include_aliases=True,
            )
            for cls in _agency_scoped_classes()
        ]
        orm_state.statement = orm_state.statement.options(*options)
    else:
        statement = orm_state.statement
        table = getattr(statement, "table", None)
        table_name = getattr(table, "name", None)
        if table_name is not None:
            for cls in _agency_scoped_classes():
                if sa_inspect(cls).local_table.name == table_name:
                    statement = statement.where(_agency_predicate(cls, agency_id))
                    orm_state.statement = statement
                    break


@event.listens_for(Session, "before_flush")
def _stamp_agency_on_insert(session, flush_context, instances):
    if not is_agency_enforcement_active():
        return
    agency_id = get_current_agency()
    classes = None
    for obj in session.new:
        state = sa_inspect(obj, raiseerr=False)
        if state is None:
            continue
        mapper = state.mapper
        if "agency_id" not in {c.key for c in mapper.column_attrs}:
            continue
        if obj.__class__.__name__ in _AGENCY_EXCLUDED:
            continue
        if getattr(obj, "agency_id", None) is None:
            if classes is None:
                classes = {cls.__name__ for cls in _agency_scoped_classes()}
            if obj.__class__.__name__ in classes:
                obj.agency_id = agency_id
