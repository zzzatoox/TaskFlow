from pydantic import (
    BaseModel,
    EmailStr,
    model_validator,
    Field,
    SecretStr,
    field_validator,
)
from typing import Self


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
