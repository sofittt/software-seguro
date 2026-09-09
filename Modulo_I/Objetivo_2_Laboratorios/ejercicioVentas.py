import requests
import time

URL = "https://chl-f788c146-8c08-44c5-b81d-b0beabc26e17-ventas.softwareseguro.com.ar/ventas/"

id_venta = 1
forbidden = 0
not_found_seguidos = 0
errores = 0

MAX_NOT_FOUND = 100
MAX_REINTENTOS = 3

while not_found_seguidos < MAX_NOT_FOUND:

    reintentos = 0
    respuesta_obtenida = False

    # Reintenta el MISMO ID si hay timeout/error de conexión
    while reintentos < MAX_REINTENTOS and not respuesta_obtenida:

        try:
            response = requests.get(
                URL,
                params={"id": id_venta},
                timeout=10
            )

            respuesta_obtenida = True

        except requests.RequestException as e:
            reintentos += 1

            print(
                f"⚠️ Error en ID {id_venta} "
                f"- Reintento {reintentos}/{MAX_REINTENTOS}"
            )
            print(e)

            # Esperamos un poco antes de volver a intentar
            time.sleep(1)

    # Si fallaron los 3 intentos
    if not respuesta_obtenida:
        print(
            f"❌ No se pudo consultar ID {id_venta} "
            f"después de {MAX_REINTENTOS} intentos"
        )

        errores += 1
        not_found_seguidos = 0
        id_venta += 1
        continue

    # -----------------------------
    # Analizamos la respuesta
    # -----------------------------

    if response.status_code == 404:

        not_found_seguidos += 1

        print(
            f"ID {id_venta}: Not Found "
            f"({not_found_seguidos}/{MAX_NOT_FOUND} consecutivos)"
        )

    else:

        # Cualquier respuesta diferente de 404
        # rompe la secuencia de Not Found
        not_found_seguidos = 0

        if response.status_code == 403:

            forbidden += 1

        else:

            print(f"\n🔎 ID INTERESANTE: {id_venta}")
            print(f"Status: {response.status_code}")
            print(f"Respuesta: {response.text[:1000]}")

    id_venta += 1


print("\n==============================")
print("🛑 100 Not Found consecutivos")
print(f"Último ID analizado: {id_venta - 1}")
print(f"Total Forbidden: {forbidden}")
print(f"IDs con error definitivo: {errores}")
print("==============================")