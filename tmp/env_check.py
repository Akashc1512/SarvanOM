import os, json
from dotenv import load_dotenv
load_dotenv()
keys = [
  'APP_ENV','LOG_LEVEL','DATABASE_URL','REDIS_URL','JWT_SECRET_KEY','MEILISEARCH_URL','MEILISEARCH_MASTER_KEY','MEILI_MASTER_KEY','QDRANT_URL','QDRANT_API_KEY'
]
print('ENV (os.getenv):')
for k in keys:
    v = os.getenv(k)
    masked = (v[:4]+'***'+v[-4:]) if v and len(v)>12 else v
    print(f'{k}={masked}')

print('\nEnvironmentManager config:')
try:
    from shared.core.config.environment_manager import get_environment_manager
    em = get_environment_manager()
    cfg = em.get_config()
    out = {
        'environment': getattr(em, 'environment', None),
        'database_url': getattr(cfg, 'database_url', None),
        'redis_url': getattr(cfg, 'redis_url', None),
        'jwt_secret_key': getattr(cfg, 'jwt_secret_key', None),
        'meilisearch_url': getattr(cfg, 'meilisearch_url', None),
        'meilisearch_master_key': getattr(cfg, 'meilisearch_master_key', None),
    }
    def mask(x):
        if x is None:
            return None
        s = str(x)
        return s if len(s)<=12 else s[:4]+'***'+s[-4:]
    for k in list(out.keys()):
        out[k] = mask(out[k])
    print(json.dumps(out, indent=2, default=str))
except Exception as e:
    print('EnvironmentManager check failed:', type(e).__name__, e)
