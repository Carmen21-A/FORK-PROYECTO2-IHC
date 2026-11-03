from collections.abc import Generator  # importa Generator para tipar la función generadora de sesiones

from sqlalchemy import create_engine  # importa create_engine para establecer la conexión con la base de datos
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker  # importa clases base para modelos y creador de sesiones ORM

from app.config import get_settings  # importa get_settings para obtener la configuración y URL de la base de datos


class Base(DeclarativeBase):  # define la clase base declarativa de la que heredarán todos los modelos de SQLAlchemy
    pass  # no añade lógica extra, sirve como base de modelos


engine = create_engine(get_settings().url_base_de_datos, pool_pre_ping=True)  # crea el motor de conexión SQLAlchemy verificando que la conexión siga viva
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)  # fábrica de sesiones vinculada al motor sin autoflush automático


def get_db() -> Generator[Session, None, None]:  # función generadora de dependencias para FastAPI que provee una sesión de base de datos
    db = SessionLocal()  # abre una nueva sesión de base de datos
    try:  # bloque try para entregar la sesión
        yield db  # entrega la sesión activa para que el endpoint la use
    finally:  # bloque finally que se ejecuta siempre al terminar la petición
        db.close()  # cierra la sesión de base de datos liberando la conexión
