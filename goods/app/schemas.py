from pydantic import BaseModel, Field


class BaseReview(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    text: str | None = None

    model_config = {"from_attributes": True}


class ReviewCreateSchema(BaseReview):
    pass


class ReviewUpdateSchema(BaseModel):
    rating: int | None = Field(None, ge=1, le=5)
    text: str | None = None


class ReviewSchema(BaseReview):
    id: int
    product_id: int
    user_id: int


class BaseProduct(BaseModel):
    name: str
    description: str | None = None
    price: float
    image_url: str | None = None

    model_config = {"from_attributes": True}


class ProductCreateSchema(BaseProduct):
    pass


class ProductUpdateSchema(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = None
    image_url: str | None = None


class ProductShortSchema(BaseProduct):
    id: int
    user_id: int
    rating: float
    reviews_count: int


class ProductSchema(ProductShortSchema):
    reviews: list[ReviewSchema] = []
