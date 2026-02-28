from pydantic import BaseModel, Field, ConfigDict


class StatusBase(BaseModel):
    title: str = Field(max_length=50, min_length=1)


class StatusCreate(StatusBase):
    pass


class StatusUpdate(StatusBase):
    title: str | None = Field(default=None, max_length=50, min_length=1)


class StatusResponse(StatusBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
