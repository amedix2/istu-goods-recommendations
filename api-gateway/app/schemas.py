from pydantic import BaseModel


class UserSchema(BaseModel):
    """Схема для создания нового пользователя и аутентефикации."""
    username: str
    password: str


class TokenSchema(BaseModel):
    """Схема для access-токена."""
    access_token: str
    token_type: str = "bearer"  # Тип токена (по умолчанию 'bearer')
