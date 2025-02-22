import os


def get_env(key: str) -> str:
    val = os.getenv(key)
    if val is None:
        raise ValueError(f"Environment variable {key} is not set.")
    return val
