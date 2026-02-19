def string_validation(value: str) -> str:
    if not value or value is None:
        return None
    return value.capitalize().strip()
