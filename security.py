

#Security utilities for password hashing and verification.

import hashlib
import os
import config

from config import salt_length, hash_iterations, hash_algorithm


def hash_password(password: str) -> tuple[str, str]:
   #salts the pssword
    salt = os.urandom(salt_length)
    hashed = hashlib.pbkdf2_hmac(
        hash_algorithm,
        password.encode('utf-8'),
        salt,
        hash_iterations
    )
    return (hashed.hex(), salt.hex())


#verifys the password agaisnt its stored hash
def verify_password(password: str, stored_hash: str, stored_salt: str) -> bool:
    try:
        computed_hash = hashlib.pbkdf2_hmac(
            hash_algorithm,
            password.encode('utf-8'),
            bytes.fromhex(stored_salt),
            hash_iterations
        )
        return computed_hash.hex() == stored_hash
    except (ValueError, TypeError):
        return False

