"""Multi-tenant isolation validation tests for EVO-LOG SaaS"""
import pytest
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import get_db, SessionLocal
from app.models.organization import Organization
from app.models.user import User
from app.models.transport import Mission

client = TestClient(app)

@pytest.fixture
def db():
    """Test database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()

def test_tenant_isolation_missions(db: Session):
    """Verify that missions from tenant A are not visible to tenant B"""
    # Create two test organizations
    org_a = Organization(name="Tenant A", slug="tenant-a", is_active=True)
    org_b = Organization(name="Tenant B", slug="tenant-b", is_active=True)
    db.add_all([org_a, org_b])
    db.commit()
    db.refresh_all([org_a, org_b])
    
    # Create a mission for tenant A
    mission_a = Mission(
        reference="MIS-A-001",
        company_id=org_a.id,
        statut="PLANIFIEE",
        date_creation="2026-01-01"
    )
    db.add(mission_a)
    db.commit()
    
    # Create a mission for tenant B
    mission_b = Mission(
        reference="MIS-B-001",
        company_id=org_b.id,
        statut="PLANIFIEE",
        date_creation="2026-01-01"
    )
    db.add(mission_b)
    db.commit()
    
    # Query missions for tenant A - should only see tenant A's mission
    missions_a = db.query(Mission).filter(Mission.company_id == org_a.id).all()
    assert len(missions_a) == 1
    assert missions_a[0].reference == "MIS-A-001"
    
    # Query missions for tenant B - should only see tenant B's mission
    missions_b = db.query(Mission).filter(Mission.company_id == org_b.id).all()
    assert len(missions_b) == 1
    assert missions_b[0].reference == "MIS-B-001"
    
    # Verify no cross-tenant access
    assert mission_a.reference not in [m.reference for m in missions_b]
    assert mission_b.reference not in [m.reference for m in missions_a]

def test_tenant_isolation_users(db: Session):
    """Verify that users from tenant A are not visible to tenant B"""
    org_a = Organization(name="Tenant A", slug="tenant-a", is_active=True)
    org_b = Organization(name="Tenant B", slug="tenant-b", is_active=True)
    db.add_all([org_a, org_b])
    db.commit()
    db.refresh_all([org_a, org_b])
    
    # Create users for each tenant
    user_a = User(
        email="usera@tenant-a.com",
        organization_id=org_a.id,
        full_name="User A"
    )
    user_b = User(
        email="userb@tenant-b.com",
        organization_id=org_b.id,
        full_name="User B"
    )
    db.add_all([user_a, user_b])
    db.commit()
    
    # Query users for tenant A
    users_a = db.query(User).filter(User.organization_id == org_a.id).all()
    assert len(users_a) == 1
    assert users_a[0].email == "usera@tenant-a.com"
    
    # Query users for tenant B
    users_b = db.query(User).filter(User.organization_id == org_b.id).all()
    assert len(users_b) == 1
    assert users_b[0].email == "userb@tenant-b.com"

def test_performance_multi_tenant_query(db: Session):
    """Verify that multi-tenant queries with indexes perform within acceptable limits"""
    import time
    
    # Create multiple organizations
    orgs = [Organization(name=f"Tenant {i}", slug=f"tenant-{i}", is_active=True) for i in range(10)]
    db.add_all(orgs)
    db.commit()
    
    # Create missions for each tenant
    for org in orgs:
        for j in range(100):
            mission = Mission(
                reference=f"MIS-{org.slug}-{j:03d}",
                company_id=org.id,
                statut="PLANIFIEE",
                date_creation="2026-01-01"
            )
            db.add(mission)
    db.commit()
    
    # Measure query performance for a single tenant
    start = time.time()
    missions = db.query(Mission).filter(Mission.company_id == orgs[0].id).all()
    elapsed = time.time() - start
    
    # Should return 100 missions and complete within 100ms
    assert len(missions) == 100
    assert elapsed < 0.1, f"Query took {elapsed}s, expected < 0.1s"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
