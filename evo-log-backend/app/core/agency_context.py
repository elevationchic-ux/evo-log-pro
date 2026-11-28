"""
Agency (agence / succursale / extension) isolation context.

Miroir de ``app.core.tenant_context`` : le contexte est resolu par requete
dans ``app.middleware.tenant_context`` a partir de
``User.current_agency_id`` et publie via contextvars pour que la couche ORM
(``app.core.agency_enforcement``) puisse scoper chaque requete.

Regles
------
- Aucun contexte agence  -> enforcement inactif (fail-open : login, workers,
  superadmin, utilisateurs sans agence selectionnee voient TOUT).
- ``agency_id`` positionne -> les modeles portant la colonne ``agency_id``
  sont filtres sur ``agency_id == courant OU agency_id IS NULL``
  (NULL = donnee partagee / non rattachee, heritee ou saisie hors contexte).
- ``bypass_agency_filter()`` desactive le filtrage pour les ecrans
  d'administration du reseau (console agences, comparatifs, superadmin).
- ``User`` est EXCLU du perimetre automatique : son ``agency_id`` est une
  affectation (agence d'appartenance), pas une donnee metier ; le filtrer
  casserait l'authentification quand l'utilisateur change d'agence active.
  Les listes d'utilisateurs par agence sont scopees explicitement dans le
  routeur ``agences``.
"""
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Optional

_current_agency_id: ContextVar[Optional[int]] = ContextVar(
    "current_agency_id", default=None
)
_bypass_depth: ContextVar[int] = ContextVar("agency_bypass_depth", default=0)


def set_current_agency(agency_id: Optional[int]) -> None:
    _current_agency_id.set(agency_id)


def get_current_agency() -> Optional[int]:
    return _current_agency_id.get()


def clear_current_agency() -> None:
    _current_agency_id.set(None)


def is_agency_bypass() -> bool:
    return _bypass_depth.get() > 0


@contextmanager
def bypass_agency_filter():
    """Desactive temporairement le filtrage agence (console reseau)."""
    token = _bypass_depth.set(_bypass_depth.get() + 1)
    try:
        yield
    finally:
        _bypass_depth.reset(token)


def is_agency_enforcement_active() -> bool:
    return (not is_agency_bypass()) and (_current_agency_id.get() is not None)
