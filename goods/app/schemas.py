from pydantic import BaseModel, Field


class BaseReview(BaseModel):
    """Базовая модель отзыва."""
    rating: int = Field(..., ge=1, le=5)
    text: str | None = None

    model_config = {"from_attributes": True}


class ReviewCreateSchema(BaseReview):
    """Схема для создания отзыва."""
    pass


class ReviewUpdateSchema(BaseModel):
    """Схема для обновления отзыва."""
    rating: int | None = Field(None, ge=1, le=5)
    text: str | None = None


class ReviewSchema(BaseReview):
    """Схема отзыва с идентификаторами."""
    id: int
    product_id: int
    user_id: int


class BaseProduct(BaseModel):
    """Базовая модель продукта."""
    name: str
    description: str | None = None
    price: float
    image_url: str | None = None

    model_config = {"from_attributes": True}


class ProductCreateSchema(BaseProduct):
    """Схема для создания продукта."""
    pass


class ProductUpdateSchema(BaseModel):
    """Схема для обновления продукта."""
    name: str | None = None
    description: str | None = None
    price: float | None = None
    image_url: str | None = None


class ProductShortSchema(BaseProduct):
    """Схема краткого представления продукта."""
    id: int
    user_id: int
    rating: float
    reviews_count: int


class ProductSchema(ProductShortSchema):
    """Схема полного продукта с отзывами."""
    reviews: list[ReviewSchema] = []
