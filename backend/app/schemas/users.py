from pydantic import (
    BaseModel,
    EmailStr,
    model_validator,
    Field,
    SecretStr,
    field_validator,
    ConfigDict,
    ValidationInfo,
)
from backend.app.utils.string_validation import (
    string_validation,
    password_match as password_match_util,
    password_validation,
)


class UserBase(BaseModel):
    email: EmailStr
    login: str = Field(max_length=20)
    last_name: str = Field(max_length=64, min_length=1)
    first_name: str = Field(max_length=64, min_length=1)
    patronymic: str | None = Field(default=None, max_length=64, min_length=1)

    @field_validator("last_name")
    @classmethod
    def validate_last_name(cls, v: str) -> str:
        return string_validation(v)

    @field_validator("first_name")
    @classmethod
    def validate_first_name(cls, v: str) -> str:
        return string_validation(v)

    @field_validator("patronymic")
    @classmethod
    def validate_patronyic(cls, v: str | None) -> str | None:
        if v is None or not v.strip():
            return None
        return string_validation(v)


class UserCreate(UserBase):
    password: SecretStr
    password_confirm: SecretStr

    @field_validator("password_confirm", mode="after")
    @classmethod
    def passwords_match(cls, value: str, info: ValidationInfo):
        pwd = info.data["password"].get_secret_value()
        pwd_confirm = value.get_secret_value()

        result = password_match_util(pwd, pwd_confirm)
        if not result:
            raise ValueError("Passwords do not match")

        return value

    @model_validator(mode="after")
    @classmethod
    def validate_password(cls, model):
        pwd = model.password.get_secret_value()
        _ = password_validation(pwd)
        return model


class UserUpdate(BaseModel):
    email: str | None = None
    login: str | None = None
    last_name: str | None = None
    first_name: str | None = None
    patronymic: str | None = None
    password: SecretStr | None = None
    password_confirm: SecretStr | None = None

    @field_validator("last_name")
    @classmethod
    def validate_last_name(cls, v: str) -> str:
        if v is None or not v.strip():
            return None
        return string_validation(v)

    @field_validator("first_name")
    @classmethod
    def validate_first_name(cls, v: str) -> str:
        if v is None or not v.strip():
            return None
        return string_validation(v)

    @field_validator("patronymic")
    @classmethod
    def validate_patronyic(cls, v: str | None) -> str | None:
        if v is None or not v.strip():
            return None
        return string_validation(v)

    @field_validator("password_confirm", mode="after")
    @classmethod
    def passwords_match(cls, value: str, info: ValidationInfo):
        if value is None:
            return value

        pwd = info.data["password"].get_secret_value()
        pwd_confirm = value.get_secret_value()

        result = password_match_util(pwd, pwd_confirm)
        if not result:
            raise ValueError("Passwords do not match")

        return value

    @model_validator(mode="after")
    @classmethod
    def validate_password(cls, model):
        if model.password is None:
            return model

        pwd = model.password.get_secret_value()
        _ = password_validation(pwd)
        return model


class UserResponse(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
