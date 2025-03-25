import json


def generate_cache_key(prefix: str, params: dict) -> str:
    """
    Generates a cache key from a prefix and a dictionary of parameters.
    """
    return f"{prefix}:{json.dumps(params, sort_keys=True, default=str)}"
