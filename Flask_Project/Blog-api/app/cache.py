import redis
from flask import current_app # To access the Flask app's configuration for Redis URL
import json

redis_client = None

def init_cache(app):
    global redis_client
    redis_client = redis.Redis.from_url(
        app.config["REDIS_URL"],
        decode_responses=True
    )

def get_cache(key):
    data = redis_client.get(key)
    return json.loads(data) if data else None

def set_cache(key, value, expiry=60): # Cache expires in 60 seconds then Cache deleted automatically and Next request → DB again
    redis_client.setex(key, expiry, json.dumps(value))

def delete_cache(key):
    redis_client.delete(key)