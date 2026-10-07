import traceback
try:
    import app.main
    from app.main import app
    paths = [getattr(r, 'path', '') for r in app.routes]
    maint = [p for p in paths if 'maintenance-industrielle' in p]
    trace = [p for p in paths if 'tracabilite' in p]
    print("maintenance mounted count:", len(maint))
    print("tracabilite mounted count:", len(trace))
    # Search any route with 'assets' or 'serialized-parts' path
    sample = [p for p in paths if 'serialized-parts' in p or '/events' in p]
    print("sample:", sample[:5])
    # Check the block actually inserted
    with open('app/main.py','r',encoding='utf-8') as f:
        s = f.read()
    print("marker maintindustrielle present:", 'expansion:maintenance_deep' in s)
    print("marker tracabilite present:", 'expansion:tracabilite_deep' in s)
    print("safe_include_router maint:", '/api/v1/maintenance-industrielle' in s)
    print("safe_include_router trace:", '/api/v1/tracabilite' in s)
except Exception:
    traceback.print_exc()
