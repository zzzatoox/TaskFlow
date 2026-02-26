def string_validation(value: str) -> str:
    return value.capitalize().strip()


def password_match(pwd: str, pwd_confirm: str) -> bool:
    if pwd != pwd_confirm:
        return False
    return True


def password_validation(pwd: str) -> bool:
    # if pwd
    # TODO: доделать валидацию пароля
    pass
