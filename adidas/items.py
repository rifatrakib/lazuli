from datetime import datetime
from typing import Union

from pydantic import BaseModel, HttpUrl, validator


class ProductCore(BaseModel):
    class Config:
        anystr_strip_whitespace = True


class ProductInformation(ProductCore):
    product_id: str
    product_name: str
    product_url: HttpUrl
    product_category: str
    available_sizes: str
    breadcrumb: str
    sense_of_fit: Union[str, None] = None
    title_of_description: Union[str, None] = None
    product_description: str
    itemization_description: str
    keywords: str
    product_rating: Union[float, None] = None
    number_of_reviews: Union[int, None] = None
    recommended_rate: Union[float, None] = None
    sense_of_fit_rate: Union[float, None] = None
    appropriation_of_length_rate: Union[float, None] = None
    material_quality_rate: Union[float, None] = None
    comfort_rate: Union[float, None] = None

    @validator("available_sizes", pre=True)
    def stringify_available_sizes(cls, v):
        return ", ".join(v)

    @validator("itemization_description", pre=True)
    def stringify_itemization_description(cls, v):
        return "\n".join([f"- {text}" for text in v])

    @validator("keywords", pre=True)
    def stringify_keywords(cls, v):
        return ", ".join([item["label"] for item in v])

    @validator("recommended_rate", pre=True)
    def extract_recommended_rate(cls, v):
        if v:
            return float(v.replace("%", "")) / 100
        return None

    @validator("sense_of_fit_rate", "appropriation_of_length_rate", "material_quality_rate", "comfort_rate", pre=True)
    def extract_rates(cls, v):
        if v:
            return float(v.split("/")[0])
        return None


class CoordinatedProduct(ProductCore):
    main_product_id: str
    main_product_name: str
    coordinated_product_number: str
    coordinated_product_name: str
    coordinated_product_price: float
    coordinated_product_page_url: HttpUrl
    coordinated_product_image_url: HttpUrl

    @validator("coordinated_product_price", pre=True)
    def extract_coordinated_product_price(cls, v):
        return float(v.replace(",", ""))

    @validator("coordinated_product_page_url", pre=True)
    def extract_coordinated_product_page_url(cls, v):
        return f"https://shop.adidas.jp/products/{v}/"

    @validator("coordinated_product_image_url", pre=True)
    def extract_coordinated_product_image_url(cls, v):
        return f"https://shop.adidas.jp{v}"


class ProductTechnology(ProductCore):
    product_id: str
    product_name: str
    technology_name: str
    description: str
    image_url: HttpUrl

    @validator("image_url", pre=True)
    def extract_image_url(cls, v):
        return f"https://shop.adidas.jp{v}"


class ProductReview(ProductCore):
    product_id: str
    product_name: str
    review_date: str
    review_rating: int
    review_title: Union[str, None] = None
    review_description: str
    reviewer_id: str

    @validator("review_rating", pre=True)
    def extract_review_rating(cls, v):
        return v.split("/")[0]

    @validator("review_date", pre=True)
    def extract_review_date(cls, v):
        date_format = "%Y年%m月%d日"
        return datetime.strptime(v, date_format).date().isoformat()
