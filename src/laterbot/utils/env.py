import os


def get_env(key: str) -> str:
    val = os.getenv(key)
    if val == None or val == "":
        raise ValueError(f"Environment variable '{key}' is not set or is empty string.")
    return val
