import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", 
        # "postgresql://postgres:postgres@db:5432/blogdb" # For docker compose, use the service name 'db' as hostname. For local development, you can use 'localhost'   
        # 'postgresql://postgres:mysecretpassword@localhost:5433/blogdb' local machine image of different port and container name."some-postgres"
        "sqlite:///blog.db"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    REDIS_URL = os.getenv(
        "REDIS_URL",
        # "redis://redis:6379/0" # Will run inside docker compose with postgres and web app.
        "redis://localhost:6379/0"  # Using docker redis container to run redis locally with project. No need to install redis on local machine. Just run docker container for redis and connect to it using localhost and port 6379. "6380:6379"  # Map to 6380 on host
    )