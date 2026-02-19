from pydantic import BaseModel, EmailStr, PositiveInt, Field, SecretStr, field_validator


class UserIn(BaseModel):
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


class UserOutput(BaseModel):
    login: str
    last_name: str
    first_name: str
    patronymic: str | None = None
