# Semilla de las pruebas E2E: deja la base con datos conocidos, siempre los mismos.
#   DATABASE_NAME=budget_e2e python semilla.py      (o desde frontend/: pnpm semilla)
# Borra TODOS los datos de esa base, por eso solo acepta bases cuyo nombre tenga "e2e".
import sys
import time
from datetime import date
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.config import get_settings
from app.logica.historial import armar_detalle_evento
from app.models import Historial, LimiteMensual, Movimiento, PresupuestoCategoria, Usuario
from app.security import hash_password

ESQUEMA = Path(__file__).resolve().parent.parent / "database" / "init" / "001_esquema.sql"  # ruta absoluta hacia el script SQL del esquema inicial

# Usuarios de prueba (tambien estan en el README)
MARTITA = {"email": "martita@presupuesto.com", "password": "martita123"}
PABLO = {"email": "pablo@presupuesto.com", "password": "pablo123"}


def crear_base_si_no_existe(url) -> None:
    servidor = create_engine(url.set(database="postgres"), isolation_level="AUTOCOMMIT")
    with servidor.connect() as conexion:
        existe = conexion.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :nombre"), {"nombre": url.database}
        ).scalar()
        if not existe:
            conexion.execute(text(f'CREATE DATABASE "{url.database}"'))
    servidor.dispose()


def sembrar() -> None:
    url = get_settings().url_base_de_datos
    if "e2e" not in (url.database or ""):
        sys.exit(f"La semilla borra todo: solo se usa en una base de pruebas (*e2e*), no en '{url.database}'.")

    crear_base_si_no_existe(url)
    engine = create_engine(url)
    hoy = date.today()

    with Session(engine) as db:
        db.connection().exec_driver_sql(ESQUEMA.read_text(encoding="utf-8"))
        # Borrar usuarios borra en cascada sus movimientos, limites, presupuestos e historial
        db.execute(text("TRUNCATE usuarios CASCADE"))
        db.execute(text("TRUNCATE eventos"))

        martita = Usuario(email=MARTITA["email"], password_hash=hash_password(MARTITA["password"]))
        pablo = Usuario(email=PABLO["email"], password_hash=hash_password(PABLO["password"]))
        db.add_all([martita, pablo])
        db.flush()

        # Martita: limite de 500 Bs y presupuesto de Transporte de 100 Bs este mes
        mes = hoy.strftime("%Y-%m")
        db.add(LimiteMensual(user_id=martita.id, mes=mes, limite=500))
        db.add(PresupuestoCategoria(user_id=martita.id, mes=mes, categoria="Transporte", monto=100))

        # Un gasto pendiente de 40 Bs y un ingreso ya pagado (su monto no se puede editar)
        movimientos = [
            Movimiento(user_id=martita.id, tipo="gasto", monto=40, categoria="Transporte",
                       descripcion="Pasaje de micro", fecha=hoy),
            Movimiento(user_id=martita.id, tipo="ingreso", monto=300, categoria="Otros",
                       descripcion="Mesada", estado="pagado", fecha=hoy),
        ]
        db.add_all(movimientos)
        db.flush()
        for m in movimientos:
            detalle = armar_detalle_evento(m.tipo, int(m.monto), m.categoria, m.descripcion)
            db.add(Historial(user_id=martita.id, movimiento_id=m.id, accion="creado", detalle=detalle))

        # Pablo: cuenta nueva, sin movimientos (sirve para el estado vacio)
        db.commit()

    engine.dispose()
    print(f"Semilla lista en '{url.database}': {MARTITA['email']} y {PABLO['email']}")


if __name__ == "__main__":
    # Si el backend esta leyendo justo cuando se vacian las tablas, PostgreSQL cancela
    # una de las dos operaciones (deadlock). Se reintenta en vez de fallar la prueba.
    for intento in range(1, 4):
        try:
            sembrar()
            break
        except OperationalError as error:
            if intento == 3:
                raise
            print(f"La base estaba ocupada ({error.orig}), reintentando...", file=sys.stderr)
            time.sleep(0.5)
