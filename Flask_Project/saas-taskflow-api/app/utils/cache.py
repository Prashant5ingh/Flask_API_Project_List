import redis
from flask import current_app # To access the Flask app's configuration for Redis URL
import json

redis_client = None

def init_cache(app):
    try:
        global redis_client
        redis_client = redis.Redis.from_url(
            app.config["REDIS_URL"],
            decode_responses=True
        )
        print("Redis cache initialized successfully.",redis_client.ping()) # Test connection to Redis
    except Exception as e:
        print(f"Failed to initialize Redis cache: {str(e)}")
        redis_client = None
def get_cache(key):
    data = redis_client.get(key)
    return json.loads(data) if data else None

def set_cache(key, value, expiry=60): # Cache expires in 60 seconds then Cache deleted automatically and Next request → DB again
    redis_client.setex(key, expiry, json.dumps(value))
    # redis_client.set(key, json.dumps(value), ex=expiry) # Alternative way to set cache with expiry using set method.

def delete_cache(pattern):
    keys = redis_client.keys(pattern)
    if keys:
        redis_client.delete(*keys)


def blacklist_token(jti): # Instead of storing the whole token, store only the jti. This way, we can check if a token is blacklisted by its unique identifier without needing to store the entire token string.
    redis_client.set(jti, "revoked", ex=3600)  # expire after token lifetime (1 hour in this case)
# can use blacklist = set() in memory for development, but Redis is better for production to handle multiple instances and persistence.
def is_token_blacklisted(jti):
    return redis_client.exists(jti)