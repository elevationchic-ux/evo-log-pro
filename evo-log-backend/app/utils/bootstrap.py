import logging

logger = logging.getLogger(__name__)

REQUIRED_TABLES = ["users", "roles", "tiers", "articles", "declarations", "missions"]


def get_missing_required_tables(existing_tables=None):
    """Vérifie si les tables requises manquent dans la base de données.
    
    Args:
        existing_tables: set ou liste de noms de tables existantes.
                         Si None, tente de les lire via SQLAlchemy inspect.
    """
    if existing_tables is None:
        try:
            from sqlalchemy import inspect
            from app.database import engine
            inspector = inspect(engine)
            existing_tables = set(inspector.get_table_names())
        except Exception as e:
            logger.warning(f"Impossible d'inspecter les tables: {e}")
            return []

    if isinstance(existing_tables, (list, tuple)):
        existing_tables = set(existing_tables)

    missing = [t for t in REQUIRED_TABLES if t not in existing_tables]
    return missing


def bootstrap_system(*args, **kwargs):
    """Initialisation du système."""
    print("🚀 EVO-LOG System Bootstrap initialized.")
    return True
