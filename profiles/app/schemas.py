from pydantic import BaseModel


class BaseUser(BaseModel):
    """Базовая модель пользователя."""
    username: str
    display_name: str
    email: str | None = None
    description: str | None = None

    model_config = {"from_attributes": True}


class UserCreateSchema(BaseUser):
    """Схема для создания пользователя."""
    pass


class UserUpdateSchema(BaseModel):
    """Схема для обновления пользователя."""
    username: str | None = None
    display_name: str | None = None
    email: str | None = None
    description: str | None = None


class UserSchema(BaseUser):
    """Схема пользователя с идентификатором."""
    user_id: int


class UserBriefSchema(BaseModel):
    """Краткая схема пользователя."""
    user_id: int
    display_name: str
