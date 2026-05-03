class Config:

    # SQLALCHEMY_DATABASE_URI = "sqlite:///users.db"
    # SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = "super-secret-key"

    JWT_ACCESS_TOKEN_EXPIRES = 3600
    # JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)  # by default, refresh tokens expire in 30 days, so this is optional to set explicitly