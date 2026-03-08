from pydantic import BaseModel, ConfigDict, Field


class TaskBase(BaseModel):
    title: str = Field(max_length=50, min_length=1)
    description: str | None = None
    executor_id: int | None = Field(default=None, ge=1)
    priority_id: int = Field(default=1, ge=1)
    status_id: int = Field(default=1, ge=1)


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=50, min_length=1)
    description: str | None = None
    owner_id: int | None = Field(default=None, ge=1)
    executor_id: int | None = Field(default=None, ge=1)
    priority_id: int | None = Field(default=None, ge=1)
    status_id: int | None = Field(default=None, ge=1)


class TaskResponse(TaskBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
