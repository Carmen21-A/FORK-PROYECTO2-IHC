from functools import lru_cache  # importa lru_cache para memorizar la instancia de configuración sin releer el archivo .env

from pydantic_settings import BaseSettings, SettingsConfigDict  # importa clases de pydantic para gestionar configuraciones con variables de entorno
from sqlalchemy.engine import URL, make_url  # importa utilidades de SQLAlchemy para parsear y manipular URLs de bases de datos


# Reemplaza a lib/env.dart: las variables se leen de backend/.env
class Settings(BaseSettings):  # define la clase de configuración que hereda de BaseSettings
    app_name: str = "Presupuesto Estudiantil"  # nombre de la aplicación con valor por defecto
    database_url: str = "postgresql+psycopg://budget:budget@localhost:5432/budget"  # URL de conexión por defecto a PostgreSQL
    # Si se define, cambia solo el nombre de la base (las pruebas E2E usan budget_e2e)
    database_name: str | None = None  # nombre de base de datos alternativo para pruebas o sobreescritura
    secret_key: str = "cambia-esta-clave-antes-de-desplegar"  # clave secreta para firmar tokens JWT
    access_token_minutes: int = 60 * 24 * 7  # duración del token de acceso en minutos (7 días)
    recovery_token_minutes: int = 60  # duración del token de recuperación de contraseña (60 minutos)
    cors_origins: str = "http://localhost:5173"  # orígenes permitidos por CORS separados por comas
    frontend_url: str = "http://localhost:5173"  # URL base de la aplicación frontend para enlaces

    # Correo para recuperar contraseña (si no se configura, el enlace sale en la consola)
    smtp_host: str | None = None  # servidor SMTP para envío de correos
    smtp_port: int = 587  # puerto del servidor SMTP por defecto (587 para TLS)
    smtp_user: str | None = None  # usuario o correo de la cuenta SMTP
    smtp_password: str | None = None  # contraseña de aplicación del correo SMTP
    smtp_from: str | None = None  # remitente visible del correo saliente
    smtp_use_tls: bool = True  # indica si se debe usar cifrado TLS para la conexión SMTP

    model_config = SettingsConfigDict(  # configuración interna del modelo de configuración
        env_file=".env",  # especifica que las variables se cargarán del archivo .env
        env_file_encoding="utf-8",  # codificación de caracteres del archivo .env
        extra="ignore",  # ignora variables adicionales que no estén definidas en la clase
    )  # fin de SettingsConfigDict

    @property
    def url_base_de_datos(self) -> URL:  # propiedad calculada que devuelve la URL de conexión final a la base de datos
        url = make_url(self.database_url)  # convierte el texto de database_url a un objeto URL de SQLAlchemy
        return url.set(database=self.database_name) if self.database_name else url  # sustituye la base de datos si se definió database_name

    @property
    def allowed_origins(self) -> list[str]:  # propiedad calculada que devuelve la lista de orígenes permitidos para CORS
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]  # divide la cadena por comas y elimina espacios


@lru_cache  # decorador que almacena en caché el resultado para devolver siempre la misma instancia
def get_settings() -> Settings:  # función para obtener la instancia única de configuración
    return Settings()  # instancia y retorna el objeto Settings
