from pwdlib import PasswordHash

# Configuración explícita y moderna
password_hasher = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hasher.hash(password)
