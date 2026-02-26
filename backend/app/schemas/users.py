from pydantic import (
    BaseModel,
    EmailStr,
    model_validator,
    Field,
    SecretStr,
    field_validator,
    ConfigDict,
)
from typing import Self
from backend.app.utils.string_validation import (
    string_validation,
    password_match as password_match_util,
)


class UserBase(BaseModel):
    email: EmailStr
    login: str
    last_name: str
    first_name: str
    patronymic: str | None = None

    @field_validator("last_name", "first_name")
    @classmethod
    def validate_names(cls, v: str) -> str:
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

    @model_validator(mode="after")
    @classmethod
    def passwords_match(cls, model):
        pwd = model.password.get_secret_value()
        pwd_confirm = model.password_confirm.get_secret_value()

        result = password_match_util(pwd, pwd_confirm)
        if not result:
            raise ValueError("Passwords do not match")

        return model


class UserUpdate(BaseModel):
    email: str | None = None
    login: str | None = None
    last_name: str | None = None
    first_name: str | None = None
    patronymic: str | None = None
    password: SecretStr | None = None

    @model_validator(mode="after")
    @classmethod
    def validate_password(cls, model):
        # TODO: доделать валидацию пароля
        pass


class UserResponse(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class User(BaseModel):
    email: EmailStr
    login: str = Field(max_length=20)
    password: SecretStr = Field(min_length=8)
    password_repeat: SecretStr = Field(min_length=8)
    last_name: str
    first_name: str
    patronymic: str | None = None
    # TODO: подумать как валидировать patronymic, если есть и не валидировать если нет

    @field_validator("last_name", "first_name", mode="before")
    @classmethod
    def strip_and_capitalize(cls, value: str) -> str:
        return value.strip().capitalize()

    @model_validator(mode="after")
    def verify_passwords_match(self) -> Self:
        if self.password.get_secret_value() != self.password_repeat.get_secret_value():
            raise ValueError("Passwords do not match")
        return self


# TODO: нужна ли?
class UserOutput(BaseModel):
    login: str
    last_name: str
    first_name: str
    patronymic: str | None = None

    class Config:
        orm_mode = True


class UserInDB(BaseModel):
    id: int
    email: EmailStr
    login: str
    password_hash: str
    last_name: str
    first_name: str
    patronymic: str | None = None

    class Config:
        orm_mode = True
