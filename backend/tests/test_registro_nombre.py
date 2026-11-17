# Registro con nombre completo (nuevo diseño de «Crear Cuenta»)
def registrar(client, **datos):  # crea una cuenta y devuelve la respuesta
    return client.post("/api/auth/register", json={"email": "lucia@test.com", "password": "secreto1", **datos})  # llama al endpoint de registro


def test_guarda_el_nombre_sin_espacios_de_mas(client):  # el nombre se limpia y se guarda
    respuesta = registrar(client, nombre="  Lucía   Pérez ")  # nombre con espacios sobrantes
    assert respuesta.status_code == 201  # la cuenta se crea
    assert respuesta.json()["user"]["nombre"] == "Lucía Pérez"  # vuelve limpio en la sesión
    token = respuesta.json()["access_token"]  # token de la sesión nueva
    yo = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})  # consulta el usuario actual
    assert yo.json()["nombre"] == "Lucía Pérez"  # quedó guardado


def test_sin_nombre_la_cuenta_igual_se_crea(client):  # la API sigue aceptando cuentas sin nombre (las antiguas no lo tienen)
    respuesta = registrar(client)  # sin el campo nombre
    assert respuesta.status_code == 201  # la cuenta se crea
    assert respuesta.json()["user"]["nombre"] is None  # sin nombre


def test_un_nombre_demasiado_largo_se_rechaza(client):  # el nombre tiene un límite de 100 letras
    respuesta = registrar(client, nombre="a" * 101)  # 101 caracteres
    assert respuesta.status_code == 422  # error de validación
