import importlib
mods = [
  'fastapi','uvicorn','httpx','pytest','services.api_gateway.main',
  'services.api_gateway.routes.health','services.api_gateway.services.sso_service']
for m in mods:
    try:
        importlib.import_module(m)
        print('OK', m)
    except Exception as e:
        print('ERR', m, type(e).__name__, e)
