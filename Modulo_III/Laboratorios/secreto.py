import itertools
import subprocess
import time
import os

# ==========================================
# CONFIGURACIÓN
# ==========================================

ZIP = r"C:\Users\sofialourdes_toledoc\Downloads\secreto.zip"
SEVEN_ZIP = r"C:\Program Files\7-Zip\7z.exe"

PATRON = "ABCCDADDDDEC"

DIGITOS = "0123456789"


# ==========================================
# VALIDACIONES
# ==========================================

if not os.path.exists(ZIP):
    print("❌ No se encontró el ZIP:")
    print(ZIP)
    exit()

if not os.path.exists(SEVEN_ZIP):
    print("❌ No se encontró 7-Zip:")
    print(SEVEN_ZIP)
    exit()


# ==========================================
# INFORMACIÓN
# ==========================================

simbolos = sorted(set(PATRON))

total = 1

for i in range(len(simbolos)):
    total *= len(DIGITOS) - i


print("=" * 50)
print("🔐 EL MEJOR SECRETO")
print("=" * 50)

print(f"\n🧩 Patrón: {PATRON}")
print(f"🔢 Símbolos: {simbolos}")
print(f"🔎 Combinaciones máximas: {total:,}")

print("\n🚀 Iniciando búsqueda...\n")


# ==========================================
# FUERZA BRUTA
# ==========================================

inicio = time.time()

probadas = 0
password_encontrada = None
mapa_encontrado = None


for permutacion in itertools.permutations(
    DIGITOS,
    len(simbolos)
):

    # Crear correspondencia:
    # A -> número
    # B -> número
    # etc.

    mapa = dict(zip(simbolos, permutacion))

    # Convertir patrón a contraseña
    password = "".join(
        mapa[letra]
        for letra in PATRON
    )

    probadas += 1


    # ======================================
    # PROBAR CONTRASEÑA
    # ======================================

    resultado = subprocess.run(
        [
            SEVEN_ZIP,
            "t",
            ZIP,
            f"-p{password}",
            "-y"
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )


    # ======================================
    # ENCONTRADA
    # ======================================

    if resultado.returncode == 0:

        password_encontrada = password
        mapa_encontrado = mapa

        break


    # ======================================
    # PROGRESO
    # ======================================

    if probadas % 100 == 0:

        transcurrido = time.time() - inicio

        velocidad = (
            probadas / transcurrido
            if transcurrido > 0
            else 0
        )

        porcentaje = (
            probadas / total
        ) * 100

        print(
            f"\r"
            f"⏳ {probadas:,}/{total:,} "
            f"({porcentaje:.1f}%) | "
            f"⚡ {velocidad:.1f} claves/s | "
            f"Última: {password}",
            end="",
            flush=True
        )


# ==========================================
# RESULTADO
# ==========================================

tiempo_total = time.time() - inicio

print("\n")


if password_encontrada:

    print("=" * 50)
    print("🎯 ¡CONTRASEÑA ENCONTRADA!")
    print("=" * 50)

    print(f"\n🔑 Password: {password_encontrada}")

    print("\n🔢 Correspondencia:")

    nombres = {
        "A": "carita",
        "B": "círculo",
        "C": "triángulo",
        "D": "corazón",
        "E": "flor"
    }

    for simbolo in simbolos:

        print(
            f"{nombres[simbolo]} ({simbolo}) "
            f"= {mapa_encontrado[simbolo]}"
        )


else:

    print("=" * 50)
    print("❌ NO SE ENCONTRÓ LA CONTRASEÑA")
    print("=" * 50)


# ==========================================
# ESTADÍSTICAS
# ==========================================

print("\n📊 Estadísticas:")
print(f"Claves probadas: {probadas:,}")
print(f"Tiempo: {tiempo_total:.2f} segundos")
print(f"Tiempo: {tiempo_total / 60:.2f} minutos")