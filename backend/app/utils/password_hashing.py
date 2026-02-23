import secrets
from pwdlib import PasswordHash
import asyncio


password_hash = PasswordHash.recommended()
DUMMY_HASH = password_hash.hash(secrets.token_hex(64))


async def verify_password_async(plain_password: str, hashed_password: str) -> bool:
    return await asyncio.to_thread(
        password_hash.verify, plain_password, hashed_password
    )


async def get_password_hash_async(password: str) -> str:
    return await asyncio.to_thread(password_hash.hash, password)
