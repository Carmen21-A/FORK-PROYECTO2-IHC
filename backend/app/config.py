from functools import lru_cache  

from pydantic_settings import BaseSettings, SettingsConfigDict  
from sqlalchemy.engine import URL, make_url  


# Reemplaza a lib/env.dart: las variables se leen de backend/.env
class Settings(BaseSettings):  
    app_name: str = "Presupuesto Estudiantil" 
    database_url: str = "postgresql+psycopg://budget:budget@localhost:5432/budget"  
    database_name: str | None = None  
    secret_key: str = "cambia-esta-clave-antes-de-desplegar"  
    access_token_minutes: int = 60 * 24 * 7  # duración del token de acceso en minutos (7 días)
    recovery_code_minutes: int = 15  # minutos que sirve el código de 4 dígitos para recuperar la contraseña
    cors_origins: str = "http://localhost:5173"  
    frontend_url: str = "http://localhost:5173"  

    # Correo para recuperar contraseña (si no se configura, el código sale en la consola)
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_user: str | None = None
    smtp_password: str | None = None
    smtp_from: str | None = None
    smtp_use_tls: bool = True
    # En la nube: Render (plan gratis) bloquea SMTP; con esta clave el correo sale por la API web de Brevo
    brevo_api_key: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",  # codificación de caracteres del archivo .env
        extra="ignore",  # ignora variables adicionales que no estén definidas en la clase
    )  # fin de SettingsConfigDict

    @property
    def url_base_de_datos(self) -> URL:
        url = make_url(self.database_url)
        return url.set(database=self.database_name) if self.database_name else url

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
