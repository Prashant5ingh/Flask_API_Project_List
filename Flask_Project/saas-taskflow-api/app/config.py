import os

class Config:
    DEFAULT_RATELIMIT = ["200 per day", "50 per hour", "5 per minute"] # Applied to all routes by default, can be overridden on specific routes using @limiter.limit() decorator. 
    
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", 
        # psql "postgresql://<username>:<password>@<host>:<port>/<database>"
        # "postgresql://postgres:postgres@db:5432/blogdb" # Only for docker compose, use the service name 'db' as hostname. For local development, you can use 'localhost'   
        # 'postgresql://postgres:mysecretpassword@localhost:5433/blogdb' local machine image of different port and container name."some-postgres" --> "set DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/blogdb"
        "postgresql://postgres:password@db:5432/taskdb"
        #"postgresql://postgres:postgres@localhost:5432/saastask" # can use the db-1 container and instead of service name 'db' use "localhost" as hostname. For local development'     
        # "sqlite:///task.db"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "secret"
    
    JWT_SECRET_KEY = "super-secret-key"
    JWT_ACCESS_TOKEN_EXPIRES = 3600

    REDIS_URL = os.getenv(
        "REDIS_URL",
        #   "redis://redis:6379/0" # Will run inside docker compose with postgres and web app.
          "redis://localhost:6379/0"  # Using docker redis container to run redis locally with project. No need to install redis on local machine. Just run docker container for redis and connect to it using localhost and port 6379. "6380:6379"  # Map to 6380 on host
        #  "redis://host.docker.internal:6379/0"  # For local development, use host.docker.internal to connect to Redis running on the host machine from within the Docker container. This allows the container to access services running on the host, such as Redis, without needing to know the host's IP address.
    )