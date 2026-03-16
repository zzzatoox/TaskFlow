from pydantic import BaseModel, Field, ConfigDict


class CommentBase(BaseModel):
    content: str = Field(max_length=10000, min_length=1)


class CommentCreate(CommentBase):
    pass


class CommentUpdate(CommentBase):
    content: str | None = Field(default=None, max_length=10000, min_length=1)


class CommentResponse(CommentBase):
    id: int
    task_id: int
    owner_id: int

    model_config = ConfigDict(from_attributes=True)
