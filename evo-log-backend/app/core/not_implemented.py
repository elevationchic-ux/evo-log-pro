"""
Helper unique pour les endpoints volontairement NON implémentés.

 Philosophie d'honnêteté produit : plutôt que de renvoyer un « faux succès »
 (données fabriquées, hash/IA/signature simulés, enregistrement qui ne
 persiste rien), on renvoie un 501 explicite indiquant la dépendance réelle
 manquante. Le frontend et les rapports peuvent ainsi distinguer une vraie
 fonctionnalité d'un stub, et l'API reste contractuelle.
"""
from fastapi import HTTPException, status


def not_implemented(fonctionnalite: str, besoin: str) -> None:
    """Lève un 501 Not Implemented avec un message précis (jamais un faux 200)."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail=(
            f"{fonctionnalite} n'est pas implémenté côté serveur. "
            f"Cette route renvoie explicitement 501 au lieu d'un faux succès. "
            f"Besoin requis : {besoin}."
        ),
    )
