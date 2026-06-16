from __future__ import annotations

from hashlib import md5, sha1, sha256


def normalize_hash(value: str | None) -> str:
    return str(value or "").strip().upper()


def hash_input_password_md5(password: str) -> str:
    return md5(password.encode("utf-8")).hexdigest().upper()


def hash_input_password_sha1(password: str) -> str:
    return sha1(password.encode("utf-8")).hexdigest().upper()


def hash_input_password_sha256(password: str) -> str:
    return sha256(password.encode("utf-8")).hexdigest().upper()


def _password_match_method(input_password: str, stored_hash: str | None) -> str:
    normalized_hash = normalize_hash(stored_hash)
    if not normalized_hash:
        return "inválido"

    if normalize_hash(input_password) == normalized_hash:
        return "direto"
    if hash_input_password_md5(input_password) == normalized_hash:
        return "md5"
    if hash_input_password_sha1(input_password) == normalized_hash:
        return "sha1"
    if hash_input_password_sha256(input_password) == normalized_hash:
        return "sha256"
    return "inválido"


def verify_database_password(input_password: str, stored_hash: str | None) -> bool:
    return _password_match_method(input_password, stored_hash) != "inválido"


def password_match_method(input_password: str, stored_hash: str | None) -> str:
    return _password_match_method(input_password, stored_hash)
