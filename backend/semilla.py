# Semilla de las pruebas E2E: deja la base con datos conocidos, siempre los mismos.
#   DATABASE_NAME=budget_e2e python semilla.py      (o desde frontend/: pnpm semilla)
# Borra TODOS los datos de esa base, por eso solo acepta bases cuyo nombre tenga "e2e".
import sys  # importa el módulo sys para acceder a argumentos y salida del sistema
import time  # importa time para pausar la ejecución en reintentos
from datetime import date  # importa date para obtener la fecha de hoy
from pathlib import Path  # importa Path para manejar rutas de archivos del sistema de forma limpia

from sqlalchemy import create_engine, text  # importa create_engine para conectar a postgres y text para escribir sentencias SQL
from sqlalchemy.exc import OperationalError  # importa OperationalError para capturar bloqueos o reintentos en postgres
from sqlalchemy.orm import Session  # importa Session para manejar transacciones ORM con la base de datos

from app.config import get_settings  # importa get_settings para obtener la URL de conexión a la base de datos
from app.logica.historial import armar_detalle_evento  # importa función para armar el texto del detalle de un evento
from app.models import Historial, LimiteMensual, Movimiento, PresupuestoCategoria, Usuario  # importa todos los modelos de tablas
from app.security import hash_password  # importa función para generar hashes seguros de contraseñas con Argon2

ESQUEMA = Path(__file__).resolve().parent.parent / "database" / "init" / "001_esquema.sql"  # ruta absoluta hacia el script SQL del esquema inicial

# Usuarios de prueba (tambien estan en el README)
MARTITA = {"email": "martita@presupuesto.com", "password": "martita123"}  # diccionario con datos del usuario de prueba Martita
PABLO = {"email": "pablo@presupuesto.com", "password": "pablo123"}  # diccionario con datos del usuario de prueba Pablo


def crear_base_si_no_existe(url) -> None:  # función que verifica y crea la base de datos en postgres si aún no existe
    servidor = create_engine(url.set(database="postgres"), isolation_level="AUTOCOMMIT")  # se conecta a la base postgres administrativa con autocommit
    with servidor.connect() as conexion:  # abre la conexión con el servidor postgres
        existe = conexion.execute(  # ejecuta consulta para comprobar si ya existe la base de datos
            text("SELECT 1 FROM pg_database WHERE datname = :nombre"), {"nombre": url.database}  # busca en la tabla pg_database
        ).scalar()  # obtiene el primer valor retornado o None
        if not existe:  # si la base de datos no existe
            conexion.execute(text(f'CREATE DATABASE "{url.database}"'))  # ejecuta el comando CREATE DATABASE para crearla
    servidor.dispose()  # cierra el pool de conexiones del servidor administrativo


def sembrar() -> None:  # función principal que vacía y puebla la base de datos de pruebas e2e
    url = get_settings().url_base_de_datos  # obtiene la URL de conexión de la base de datos actual
    if "e2e" not in (url.database or ""):  # seguridad: verifica que el nombre de la base contenga 'e2e'
        sys.exit(f"La semilla borra todo: solo se usa en una base de pruebas (*e2e*), no en '{url.database}'.")  # cancela si no es de pruebas

    crear_base_si_no_existe(url)  # asegura que la base de datos de pruebas exista
    engine = create_engine(url)  # crea el motor de conexión hacia la base de datos de pruebas
    hoy = date.today()  # obtiene la fecha de hoy para inicializar los movimientos

    with Session(engine) as db:  # abre una sesión transaccional con la base de datos
        db.connection().exec_driver_sql(ESQUEMA.read_text(encoding="utf-8"))  # ejecuta el archivo 001_esquema.sql para asegurar tablas
        # Borrar usuarios borra en cascada sus movimientos, limites, presupuestos e historial
        db.execute(text("TRUNCATE usuarios CASCADE"))  # vacía todas las tablas en cascada para comenzar desde cero

        martita = Usuario(email=MARTITA["email"], password_hash=hash_password(MARTITA["password"]))  # crea el usuario Martita con su contraseña hasheada
        pablo = Usuario(email=PABLO["email"], password_hash=hash_password(PABLO["password"]))  # crea el usuario Pablo con su contraseña hasheada
        db.add_all([martita, pablo])  # agrega ambos usuarios a la sesión
        db.flush()  # sincroniza con la base para obtener sus ids generados

        # Martita: limite de 500 Bs y presupuesto de Transporte de 100 Bs este mes
        mes = hoy.strftime("%Y-%m")  # obtiene el mes actual en formato 'YYYY-MM'
        db.add(LimiteMensual(user_id=martita.id, mes=mes, limite=500))  # fija límite mensual de 500 Bs para Martita
        db.add(PresupuestoCategoria(user_id=martita.id, mes=mes, categoria="Transporte", monto=100))  # fija presupuesto de 100 Bs en Transporte

        # Un gasto pendiente de 40 Bs y un ingreso ya pagado (su monto no se puede editar)
        movimientos = [  # lista con los dos movimientos iniciales de Martita
            Movimiento(user_id=martita.id, tipo="gasto", monto=40, categoria="Transporte",  # gasto pendiente de pasaje de micro
                       descripcion="Pasaje de micro", fecha=hoy),  # descripción y fecha de hoy
            Movimiento(user_id=martita.id, tipo="ingreso", monto=300, categoria="Otros",  # ingreso pagado de mesada
                       descripcion="Mesada", estado="pagado", fecha=hoy),  # descripción, estado pagado y fecha
        ]  # fin de lista de movimientos
        db.add_all(movimientos)  # agrega los movimientos a la sesión
        db.flush()  # envía a la base para obtener sus ids
        for m in movimientos:  # recorre cada movimiento para registrar su creación en el historial
            detalle = armar_detalle_evento(m.tipo, int(m.monto), m.categoria, m.descripcion)  # genera el texto descriptivo del movimiento
            db.add(Historial(user_id=martita.id, movimiento_id=m.id, accion="creado", detalle=detalle))  # agrega el evento al historial

        # Pablo: cuenta nueva, sin movimientos (sirve para el estado vacio)
        db.commit()  # confirma todas las operaciones guardando la semilla en la base de datos

    engine.dispose()  # libera y cierra las conexiones del motor
    print(f"Semilla lista en '{url.database}': {MARTITA['email']} y {PABLO['email']}")  # imprime mensaje de éxito en terminal


if __name__ == "__main__":  # punto de entrada si el archivo se ejecuta directamente desde la consola
    # Si el backend esta leyendo justo cuando se vacian las tablas, PostgreSQL cancela
    # una de las dos operaciones (deadlock). Se reintenta en vez de fallar la prueba.
    for intento in range(1, 4):  # realiza hasta 3 intentos por si la base estaba ocupada
        try:  # bloque de intento
            sembrar()  # ejecuta la siembra de la base
            break  # si se completó con éxito, sale del bucle
        except OperationalError as error:  # captura posibles bloqueos transitorios en postgres
            if intento == 3:  # si falló en el tercer intento
                raise  # relanza el error para alertar de la falla
            print(f"La base estaba ocupada ({error.orig}), reintentando...", file=sys.stderr)  # muestra aviso de reintento en stderr
            time.sleep(0.5)  # espera medio segundo antes de volver a intentar
