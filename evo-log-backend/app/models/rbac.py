"""Compat SaaS : enums de niveau de role et de plan tenant.

HISTORIQUE / NETTOYAGE
----------------------
Ce module definissait autrefois des classes ORM ``Tenant``, ``Role``,
``Permission`` et ``UserRoleAssignment`` en DOUBLON des modeles reels de
:mod:`app.models.user` (tables ``roles`` / ``permissions`` declarees avec
``extend_existing=True``). Ces classes n'etaient importees nulle part et
entrent en collision avec le vrai mapping ORM (relationship ``User.tenant``
inexistante -> echec de ``configure_mappers``). Elles ont ete supprimees.

La source de verite unique reste :
- ``User`` / ``Role`` / ``Permission``  -> :mod:`app.models.user`
- ``Company`` (le "tenant")             -> :mod:`app.models.tenant`
- Habilitations avancees                -> :mod:`app.models.accreditation`
- Moteur d'autorisation                 -> :mod:`app.core.permissions`

Les enums ci-dessous sont conservés car ils documentent la nomenclature SaaS
et restent reutilisables par les schemas Pydantic.
"""
import enum


class TenantPlan(str, enum.Enum):
    STARTER = "STARTER"
    PROFESSIONNEL = "PROFESSIONNEL"
    ENTERPRISE = "ENTERPRISE"
    CUSTOM = "CUSTOM"


class UserRoleLevel(str, enum.Enum):
    SUPER_ADMIN = "SUPER_ADMIN"       # Accès total multi-tenant (EVO-LOG interne)
    ADMIN = "ADMIN"                   # Accès total à son tenant
    MANAGER = "MANAGER"               # Accès à ses modules assignés + reporting
    SUPERVISEUR = "SUPERVISEUR"       # Validation des opérations
    OPERATEUR = "OPERATEUR"           # Saisie et consultation
    CHAUFFEUR = "CHAUFFEUR"           # Mobile uniquement : missions, e-POD
    CLIENT_B2B = "CLIENT_B2B"         # Portail B2B : lecture seule suivi dossier
