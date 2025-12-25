from pydantic import BaseModel


class BaseUser(BaseModel):
    username: str
    display_name: str
    email: str
    description: str | None = None

    model_config = {"from_attributes": True}


class UserCreateSchema(BaseUser):
    pass


class UserUpdateSchema(BaseModel):
    username: str | None = None
    display_name: str | None = None
    email: str | None = None
    description: str | None = None


class UserSchema(BaseUser):
    user_id: int


class UserBriefSchema(BaseModel):
    user_id: int
    display_name: str
