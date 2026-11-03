"""Copia los datos de Supabase al PostgreSQL nuevo.

Supabase por dentro es PostgreSQL, asi que se lee directo de su base:
  - auth.users            -> usuarios (las contraseñas bcrypt siguen funcionando)
  - movimientos           -> movimientos
  - limites_mensuales     -> limites_mensuales
      (las filas 'YYYY-MM#Categoria' del respaldo viejo -> presupuestos_categoria)
  - presupuestos_categoria-> presupuestos_categoria
  - historial             -> historial

Se conservan los mismos id, asi que se puede correr varias veces sin duplicar.
Supabase no se modifica: solo se lee.

Uso (desde la carpeta database/):
  pip install "psycopg[binary]"
  python migracion/migrar_desde_supabase.py \
      --origen  "postgresql://postgres.xxxx:CLAVE@aws-0-xx.pooler.supabase.com:5432/postgres" \
      --destino "postgresql://budget:budget@localhost:5432/budget"

La cadena de --origen esta en Supabase: Project Settings > Database > Connection string (URI).
"""

import argparse
import re

import psycopg

CATEGORIAS = {"Transporte", "Comida", "Estudios", "Ocio", "Otros"}
PATRON_MES = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")


def columnas(conexion, esquema: str, tabla: str) -> set[str]:
    filas = conexion.execute(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_schema = %s AND table_name = %s",
        (esquema, tabla),
    ).fetchall()
    return {fila[0] for fila in filas}


def leer(conexion, esquema: str, tabla: str, campos: dict[str, str]) -> list[dict]:
    """campos = {nombre_destino: expresion_sql}. Si la columna no existe se usa NULL."""
    existentes = columnas(conexion, esquema, tabla)
    if not existentes:
        print(f"  (no existe {esquema}.{tabla}, se omite)")
        return []
    partes = []
    for destino, expresion in campos.items():
        columna = expresion.split("(")[-1].split(",")[0].split(")")[0].strip()
        partes.append(f"{expresion if columna in existentes else 'NULL'} AS {destino}")
    filas = conexion.execute(
        f"SELECT {', '.join(partes)} FROM {esquema}.{tabla}"
    ).fetchall()
    return [dict(zip(campos, fila)) for fila in filas]


def insertar(destino, tabla: str, filas: list[dict], conflicto: str = "(id)") -> int:
    if not filas:
        return 0
    nombres = [k for k in filas[0] if any(f[k] is not None for f in filas)]
    marcadores = ", ".join(["%s"] * len(nombres))
    sql = (
        f"INSERT INTO {tabla} ({', '.join(nombres)}) VALUES ({marcadores}) "
        f"ON CONFLICT {conflicto} DO NOTHING"
    )
    antes = destino.execute(f"SELECT COUNT(*) FROM {tabla}").fetchone()[0]
    with destino.cursor() as cursor:
        cursor.executemany(sql, [[f[n] for n in nombres] for f in filas])
    return destino.execute(f"SELECT COUNT(*) FROM {tabla}").fetchone()[0] - antes


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--origen", required=True, help="URI de la base de Supabase")
    parser.add_argument("--destino", required=True, help="URI del PostgreSQL nuevo")
    args = parser.parse_args()

    with psycopg.connect(args.origen) as origen, psycopg.connect(args.destino) as destino:
        print("Leyendo Supabase...")
        usuarios = [
            u
            for u in leer(origen, "auth", "users", {
                "id": "id",
                "email": "lower(email)",
                "password_hash": "encrypted_password",
                "created_at": "created_at",
            })
            if u["email"] and u["password_hash"]
        ]
        ids = {u["id"] for u in usuarios}

        movimientos = leer(origen, "public", "movimientos", {
            "id": "id",
            "user_id": "user_id",
            "tipo": "tipo",
            "monto": "monto",
            "categoria": "categoria",
            "descripcion": "coalesce(descripcion, '')",
            "estado": "coalesce(estado, 'pendiente')",
            "fecha": "fecha",
            "created_at": "created_at",
        })
        limites_y_respaldo = leer(origen, "public", "limites_mensuales", {
            "id": "id",
            "user_id": "user_id",
            "mes": "mes",
            "limite": "limite",
            "created_at": "created_at",
        })
        presupuestos = leer(origen, "public", "presupuestos_categoria", {
            "id": "id",
            "user_id": "user_id",
            "mes": "mes",
            "categoria": "categoria",
            "monto": "monto",
            "created_at": "created_at",
            "updated_at": "updated_at",
        })
        historial = leer(origen, "public", "historial", {
            "id": "id",
            "user_id": "user_id",
            "movimiento_id": "movimiento_id",
            "accion": "accion",
            "detalle": "coalesce(detalle, '')",
            "created_at": "created_at",
        })

        # Separa los limites reales de los presupuestos guardados como 'YYYY-MM#Categoria'
        limites = []
        for fila in limites_y_respaldo:
            mes = fila["mes"] or ""
            if "#" in mes:
                mes_real, categoria = mes.split("#", 1)
                if PATRON_MES.match(mes_real) and categoria in CATEGORIAS:
                    presupuestos.append({
                        "id": fila["id"],
                        "user_id": fila["user_id"],
                        "mes": mes_real,
                        "categoria": categoria,
                        "monto": fila["limite"],
                        "created_at": fila["created_at"],
                        "updated_at": fila["created_at"],
                    })
            elif PATRON_MES.match(mes):
                limites.append(fila)

        def propios(filas):
            return [f for f in filas if f["user_id"] in ids]

        print("Escribiendo en PostgreSQL...")
        resumen = {
            "usuarios": insertar(destino, "usuarios", usuarios),
            "movimientos": insertar(destino, "movimientos", propios(movimientos)),
            "limites_mensuales": insertar(
                destino, "limites_mensuales", propios(limites), "(user_id, mes)"
            ),
            "presupuestos_categoria": insertar(
                destino, "presupuestos_categoria", propios(presupuestos), "(user_id, mes, categoria)"
            ),
            "historial": insertar(destino, "historial", propios(historial)),
        }
        destino.commit()

    print("Listo. Filas nuevas copiadas:")
    for tabla, cantidad in resumen.items():
        print(f"  {tabla:<24} {cantidad}")


if __name__ == "__main__":
    main()
