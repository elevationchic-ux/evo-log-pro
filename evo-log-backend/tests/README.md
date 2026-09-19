# EVO-LOG Backend Tests

This directory contains unit and integration tests for the EVO-LOG backend application.

## Test Structure

```
tests/
├── conftest.py              # Pytest configuration and fixtures
├── unit/                    # Unit tests for services and models
│   ├── test_finance.py      # Finance module tests (OHADA accounting)
│   ├── test_qhse.py         # QHSE module tests (Quality, Health, Safety, Environment)
│   ├── test_documents.py    # Documents module tests (EDM)
│   ├── test_maintenance_gmao.py  # Maintenance GMAO module tests
│   ├── test_integration.py  # Integration module tests (SYDONIA+, PCS, etc.)
│   ├── test_notifications.py # Notifications module tests (multi-channel)
│   ├── test_reporting.py    # Reporting module tests (dashboard, KPIs)
│   └── test_acquisition.py  # Acquisition module tests (procurement)
└── integration/             # Integration tests (to be added)
```

## Running Tests

### Run all tests
```bash
cd EVO-LOG-backend
pytest
```

### Run specific test file
```bash
cd EVO-LOG-backend
pytest tests/unit/test_finance.py
```

### Run with coverage
```bash
cd EVO-LOG-backend
pytest --cov=app --cov-report=html
```

### Run with verbose output
```bash
cd EVO-LOG-backend
pytest -v
```

## Test Coverage

The following modules have unit tests:

1. **Finance** - OHADA accounting, VAT, withholding tax, invoices, payments
2. **QHSE** - Risk analysis, prevention actions, work accidents, audits
3. **Documents** - EDM, workflows, electronic signatures, OCR
4. **Maintenance GMAO** - Maintenance orders, equipment, calibration, MTBF/MTTR
5. **Integration** - SYDONIA+, Guichet Unique, PCS, banking integrations
6. **Notifications** - Email, SMS, WhatsApp, push notifications, templates
7. **Reporting** - Executive dashboard, KPIs, reports, exports
8. **Acquisition** - Tenders, framework contracts, purchase orders, receptions

## Fixtures

Available fixtures in `conftest.py`:

- `db` - Fresh database session for each test
- `client` - FastAPI test client with database override
- `sample_user` - Sample user for authentication tests
- `auth_headers` - Authentication headers for API tests

## Test Conventions

- Test classes are named `Test<ServiceName>Service`
- Test methods use `snake_case` and describe the action being tested
- Each test creates necessary data and validates the expected outcome
- Tests use the actual service methods, not direct database manipulation

## Adding New Tests

When adding tests for a new module:

1. Create a new test file in `tests/unit/`
2. Import the models and services for the module
3. Create test classes for each service
4. Test create, update, and delete operations
5. Add the test file to this README

## Cameroon/CEMAC Specific Tests

Tests verify compliance with:
- OHADA accounting standards
- Cameroon/CEMAC customs procedures
- Local tax regulations (VAT 19.25%, withholding tax, minimum corporate tax)
- Currency handling (XAF - Central African CFA Franc)

## Statut vérifié au 20 septembre 2026

Ce document contient des éléments historiques ou de conception. Il ne constitue pas une certification de production. La source de vérité actuelle est [ETAT_REEL_2026-09-20.md](./ETAT_REEL_2026-09-20.md), qui distingue les fonctionnalités vérifiées, les endpoints réellement persistants et les validations encore manquantes. Toute mention antérieure de « 100 % », « certifié », « production-ready », « zéro mock » ou « aucun bug » doit être lue comme historique tant qu’elle n’est pas couverte par un test reproductible et une persistance backend vérifiable.
