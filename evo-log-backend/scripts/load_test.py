"""Test de charge EVO-LOG : smoke en processus ou cible externe.

Modes :
  python scripts/load_test.py                     -> in-process ASGI (httpx),
     frappe l'app FastAPI directement (schema cree si absent, auth ignoree) :
     smoke de charge reproductible sans infrastructure.
  python scripts/load_test.py --base-url URL --token JWT --users 50 --requests 20
     -> charge HTTP reelle contre Railway/local (endpoints proteges par JWT).

Sortie : latences p50/p95/p99, debit, taux d'erreur. Code de sortie != 0
si le taux d'erreur depasse --max-error-rate (defaut 5%).
"""
from __future__ import annotations

import argparse
import asyncio
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import httpx  # noqa: E402

ENDPOINTS = [
    "/api/v1/health",
    "/api/v1/finance/kpis",
    "/api/v1/finance/analytics/chart-data",
    "/api/v1/finance/factures",
    "/api/v1/finance/encaissements",
    "/api/v1/transport/kpis",
    "/api/v1/magasin/kpis",
    "/api/v1/magasin/entrepots/occupation",
]


def percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    k = min(len(ordered) - 1, int(round((pct / 100.0) * (len(ordered) - 1))))
    return ordered[k]


async def worker(
    client: httpx.AsyncClient,
    base: str,
    endpoint: str,
    count: int,
    latencies: list[float],
    errors: list[str],
    semaphore: asyncio.Semaphore,
) -> None:
    for _ in range(count):
        async with semaphore:
            t0 = time.perf_counter()
            try:
                resp = await client.get(f"{base}{endpoint}")
                dt = (time.perf_counter() - t0) * 1000.0
                latencies.append(dt)
                if resp.status_code >= 400:
                    errors.append(f"{endpoint} -> HTTP {resp.status_code}")
            except Exception as exc:  # reseau, timeout...
                dt = (time.perf_counter() - t0) * 1000.0
                latencies.append(dt)
                errors.append(f"{endpoint} -> {type(exc).__name__}: {exc}")


async def run_in_process(users: int, per_endpoint: int) -> tuple[list[float], list[str]]:
    """Charge via le transport ASGI (sans serveur, sans network)."""
    from app.core import security
    from app.main import app as fastapi_app
    import app.models  # noqa: F401  (enregistre le metadata complet)

    class _DummyUser:
        id = 1
        username = "loadtest"
        is_superuser = True
        company_id = None
        organization_id = None
        roles: list[str] = []

    fastapi_app.dependency_overrides[security.get_current_user] = lambda: _DummyUser()

    # Le lifespan n'est pas declenche par ASGITransport : creer le schema.
    from app.core.database import Base, engine
    Base.metadata.create_all(bind=engine)

    transport = httpx.ASGITransport(app=fastapi_app)
    latencies: list[float] = []
    errors: list[str] = []
    semaphore = asyncio.Semaphore(users)
    async with httpx.AsyncClient(transport=transport, base_url="http://loadtest", timeout=30.0) as client:
        t0 = time.perf_counter()
        await asyncio.gather(
            *(worker(client, "", ep, per_endpoint, latencies, errors, semaphore) for ep in ENDPOINTS)
        )
        wall = time.perf_counter() - t0
    fastapi_app.dependency_overrides.clear()
    return latencies, errors, wall


async def run_external(
    base_url: str, token: str, users: int, per_endpoint: int
) -> tuple[list[float], list[str], float]:
    latencies: list[float] = []
    errors: list[str] = []
    semaphore = asyncio.Semaphore(users)
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    async with httpx.AsyncClient(headers=headers, timeout=30.0) as client:
        t0 = time.perf_counter()
        await asyncio.gather(
            *(worker(client, base_url.rstrip("/"), ep, per_endpoint, latencies, errors, semaphore) for ep in ENDPOINTS)
        )
        wall = time.perf_counter() - t0
    return latencies, errors, wall


def main() -> None:
    parser = argparse.ArgumentParser(description="Test de charge EVO-LOG")
    parser.add_argument("--base-url", default=None, help="URL du backend (sinon mode ASGI in-process)")
    parser.add_argument("--token", default="", help="JWT Bearer pour le mode externe")
    parser.add_argument("--users", type=int, default=20, help="concurrency (simultanee max)")
    parser.add_argument("--requests", type=int, default=10, help="requetes par endpoint")
    parser.add_argument("--max-error-rate", type=float, default=5.0, help="pourcentage d'erreurs tolere")
    args = parser.parse_args()

    total_expected = len(ENDPOINTS) * args.requests
    if args.base_url:
        latencies, errors, wall = asyncio.run(
            run_external(args.base_url, args.token, args.users, args.requests)
        )
    else:
        latencies, errors, wall = asyncio.run(run_in_process(args.users, args.requests))

    n = len(latencies)
    err_rate = (len(errors) / total_expected * 100.0) if total_expected else 0.0
    rps = n / wall if wall > 0 else 0.0

    print("=" * 60)
    print("RESULTATS TEST DE CHARGE")
    print("=" * 60)
    print(f"Mode            : {'HTTP externe ' + args.base_url if args.base_url else 'ASGI in-process'}")
    print(f"Endpoints       : {len(ENDPOINTS)} x {args.requests} requetes")
    print(f"Requetes OK     : {n - len(errors)}/{total_expected}")
    print(f"Latence p50     : {percentile(latencies, 50):.1f} ms")
    print(f"Latence p95     : {percentile(latencies, 95):.1f} ms")
    print(f"Latence p99     : {percentile(latencies, 99):.1f} ms")
    print(f"Debit           : {rps:.1f} req/s")
    print(f"Taux d'erreur   : {err_rate:.1f}%")
    if errors:
        print("-" * 60)
        print("Premieres erreurs (max 10) :")
        for e in errors[:10]:
            print("  ", e)
    print("=" * 60)
    if err_rate > args.max_error_rate:
        print(f"ECHEC : taux d'erreur {err_rate:.1f}% > {args.max_error_rate:.1f}%")
        sys.exit(1)
    print("SMOKE PASSE")


if __name__ == "__main__":
    main()
