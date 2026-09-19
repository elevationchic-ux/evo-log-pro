"""Checks for ambiguous FastAPI route registrations."""

from collections import defaultdict
from typing import Any, Dict, List, Tuple


def duplicate_routes(app: Any) -> Dict[Tuple[str, str], List[str]]:
    """Return duplicate method/path registrations with their endpoint names."""

    routes: Dict[Tuple[str, str], List[str]] = defaultdict(list)
    for route in app.routes:
        path = getattr(route, "path", None)
        methods = getattr(route, "methods", None) or set()
        endpoint = getattr(getattr(route, "endpoint", None), "__name__", repr(route))
        if path is None:
            continue
        for method in methods:
            routes[(method.upper(), path)].append(endpoint)
    return {key: endpoints for key, endpoints in routes.items() if len(endpoints) > 1}


def assert_no_duplicate_routes(app: Any) -> None:
    duplicates = duplicate_routes(app)
    if duplicates:
        details = ", ".join(f"{method} {path}: {names}" for (method, path), names in duplicates.items())
        raise AssertionError(f"duplicate API routes detected: {details}")
