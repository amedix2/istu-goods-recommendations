from pydantic import BaseModel


class BaseMedia(BaseModel):
    file_path: str
    file_path_thumb: str
    description: str | None = None
    is_avatar: bool = False

    model_config = {"from_attributes": True}


class MediaSchema(BaseMedia):
    id: int
    user_id: int


class MediaCreateSchema(BaseMedia):
    pass


class MediaUpdateSchema(BaseModel):
    file_path: str | None = None
    file_path_thumb: str | None = None
    description: str | None = None
    is_avatar: bool | None = None


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
    media: list[MediaSchema]


class UserBriefSchema(BaseModel):
    user_id: int
    display_name: str
    avatar_thumb: str | None
