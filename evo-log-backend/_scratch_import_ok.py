import traceback
try:
    from app.models import maintenance_deep, tracabilite_deep
    print("maintenance entities:", [n for n in dir(maintenance_deep) if n[0].isupper()])
    print("tracabilite entities:", [n for n in dir(tracabilite_deep) if n[0].isupper()])
    print("---")
    from app.models.maintenance_deep import TechnicalAsset, SparePartCatalog, PartInventory, PartMovement, WorkOrderPart
    print("asset tbl=", TechnicalAsset.__tablename__)
    print("cat=", SparePartCatalog.__tablename__)
    print("inv=", PartInventory.__tablename__)
    print("mvt=", PartMovement.__tablename__)
    print("wop=", WorkOrderPart.__tablename__)
    # check FKs resolve
    eng = None
    from app.core.database import engine
    eng = engine
    maintenance_deep.Base.metadata.create_all(bind=eng, tables=[
        TechnicalAsset.__table__, SparePartCatalog.__table__,
        PartInventory.__table__, PartMovement.__table__, WorkOrderPart.__table__], checkfirst=True)
    print("create_all OK")
except Exception:
    traceback.print_exc()
