import json

from itemadapter import ItemAdapter
from scrapy import signals

from adidas.preprocessors import (
    process_product_coordinates,
    process_product_information,
    process_product_media,
    process_product_reviews,
    process_product_sizes,
    process_product_technologies,
)
from adidas.transformers import generate_product_spreadsheet
from adidas.utils import create_directory


class AdidasPipeline:
    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
        crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
        return pipeline

    def spider_opened(self, spider):
        prefixes = [
            "product-information",
            "product-media",
            "product-coordinates",
            "product-sizes",
            "product-technologies",
            "product-reviews",
        ]
        location = create_directory("data/jsonlines", "jl", prefixes)

        self.product_information_filename = "product-information-latest.jl"
        self.product_information_file = open(f"{location}/{self.product_information_filename}", "w", encoding="utf-8")

        self.product_media_filename = "product-media-latest.jl"
        self.product_media_file = open(f"{location}/{self.product_media_filename}", "w", encoding="utf-8")

        self.product_coordinates_filename = "product-coordinates-latest.jl"
        self.product_coordinates_file = open(f"{location}/{self.product_coordinates_filename}", "w", encoding="utf-8")

        self.product_size_filename = "product-sizes-latest.jl"
        self.product_size_file = open(f"{location}/{self.product_size_filename}", "w", encoding="utf-8")

        self.product_technology_filename = "product-technologies-latest.jl"
        self.product_technology_file = open(f"{location}/{self.product_technology_filename}", "w", encoding="utf-8")

        self.product_review_filename = "product-reviews-latest.jl"
        self.product_review_file = open(f"{location}/{self.product_review_filename}", "w", encoding="utf-8")

    def spider_closed(self, spider):
        self.product_information_file.close()
        self.product_media_file.close()
        self.product_coordinates_file.close()
        self.product_size_file.close()
        self.product_technology_file.close()
        self.product_review_file.close()
        generate_product_spreadsheet()

    def process_item(self, item, spider):
        product = ItemAdapter(item).asdict()

        product_information = process_product_information(product)
        product_information = json.dumps(product_information, ensure_ascii=False) + "\n"
        self.product_information_file.write(product_information)

        if product["api_info"]["product"]["article"]["image"]:
            product_media = process_product_media(product)
            for media_record in product_media:
                media_record = json.dumps(media_record, ensure_ascii=False) + "\n"
                self.product_media_file.write(media_record)

        if product["api_info"]["product"]["article"]["coordinates"]:
            product_coordinates = process_product_coordinates(product)
            for product_coordinate in product_coordinates:
                product_coordinate = json.dumps(product_coordinate, ensure_ascii=False) + "\n"
                self.product_coordinates_file.write(product_coordinate)

        if product["size_chart"]:
            product_sizes = process_product_sizes(product)
            for product_size in product_sizes:
                product_size = json.dumps(product_size, ensure_ascii=False) + "\n"
                self.product_size_file.write(product_size)

        if product["api_info"]["product"]["model"]["description"]["technology"]:
            product_technologies = process_product_technologies(product)
            for product_technology in product_technologies:
                product_technology = json.dumps(product_technology, ensure_ascii=False) + "\n"
                self.product_technology_file.write(product_technology)

        if product["review_data"]:
            product_reviews = process_product_reviews(product)
            for product_review in product_reviews:
                product_review = json.dumps(product_review, ensure_ascii=False) + "\n"
                self.product_review_file.write(product_review)

        return f"Product from {product['product_data']['url']} scraped successfully."
