def string_validation(value: str | list) -> str:
    if isinstance(value, list):
        return [string_validation(item) for item in value]
    if isinstance(value, str):
        return value.capitalize().strip()
    raise TypeError("Value must be a string or a list of strings")


def password_match(pwd: str, pwd_confirm: str) -> bool:
    if pwd != pwd_confirm:
        return False
    return True


def password_validation(pwd: str) -> bool:
    SpecialSym = ["$", "@", "#", "%"]

    if not any(char.isupper() for char in pwd):
        raise ValueError("Password should have at least one uppercase letter")

    if not any(char.islower() for char in pwd):
        raise ValueError("Password should have at least one lowercase letter")

    if not any(char in SpecialSym for char in pwd):
        raise ValueError("Password should have at least one of the symbols $@#%")

    if not any(char.isdigit() for char in pwd):
        raise ValueError("Password should have at least one numeral")

    if len(pwd) < 8:
        raise ValueError("Password must be longer than 8  characters")

    return True
