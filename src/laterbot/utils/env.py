import os


def get_env(key: str) -> str:
    val = os.getenv(key)
    if val is None or val is "":
        raise ValueError(f"Environment variable '{key}' is not set or is empty string.")
    return val
