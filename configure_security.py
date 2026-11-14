
import os
from datetime import timedelta
from dotenv import load_dotenv


def configure_security(app):
    load_dotenv()

    secret_key = os.getenv("FLASK_SECRET_KEY")
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")

    if not secret_key or len(secret_key) < 32:
        raise RuntimeError(
            "FLASK_SECRET_KEY eksik veya çok kısa. .env dosyasını kontrol edin."
        )

    if not admin_email or not admin_password:
        raise RuntimeError(
            "ADMIN_EMAIL veya ADMIN_PASSWORD .env dosyasında tanımlanmamış."
        )

    app.config.update(
        SECRET_KEY=secret_key,
        ADMIN_EMAIL=admin_email,
        ADMIN_PASSWORD=admin_password,

        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=os.getenv(
            "SESSION_COOKIE_SECURE", "false"
        ).lower() == "true",

        PERMANENT_SESSION_LIFETIME=timedelta(hours=12),
        SESSION_REFRESH_EACH_REQUEST=True,

        DEBUG=os.getenv("FLASK_DEBUG", "false").lower() == "true"
    )
