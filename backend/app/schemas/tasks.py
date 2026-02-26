from pydantic import BaseModel, ConfigDict


class TaskBase(BaseModel):
    title: str
    description: str | None = None
    owner_id: int
    executor_id: int | None = None
    priority: int


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    pass


class TaskResponse(TaskBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
