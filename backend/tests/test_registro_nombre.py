# Registro con nombre completo (nuevo diseño de «Crear Cuenta»)
def registrar(client, **datos):
    return client.post("/api/auth/register", json={"email": "lucia@test.com", "password": "secreto1", **datos})


def test_guarda_el_nombre_sin_espacios_de_mas(client):
    respuesta = registrar(client, nombre="  Lucía   Pérez ")
    assert respuesta.status_code == 201
    assert respuesta.json()["user"]["nombre"] == "Lucía Pérez"
    token = respuesta.json()["access_token"]
    yo = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert yo.json()["nombre"] == "Lucía Pérez"


def test_sin_nombre_la_cuenta_igual_se_crea(client):
    respuesta = registrar(client)
    assert respuesta.status_code == 201
    assert respuesta.json()["user"]["nombre"] is None


def test_un_nombre_demasiado_largo_se_rechaza(client):
    respuesta = registrar(client, nombre="a" * 101)
    assert respuesta.status_code == 422
