from pydantic import BaseModel, Field, ConfigDict


class PriorityBase(BaseModel):
    title: str = Field(max_length=50, min_length=1)


class PriorityCreate(PriorityBase):
    pass


class PriorityUpdate(PriorityBase):
    title: str | None = Field(default=None, max_length=50, min_length=1)


class PriorityResponse(PriorityBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
