import json
from datetime import datetime
from pathlib import Path

from itemadapter import ItemAdapter
from pymongo import MongoClient
from scrapy import signals
from scrapy.exporters import CsvItemExporter

from services.etl import (
    process_product_coordinates,
    process_product_reviews,
    process_product_sizes,
    process_product_technologies,
    process_single_product,
)


class CSVPipeline:
    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
        crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
        return pipeline

    def spider_opened(self, spider):
        scraping_date = datetime.utcnow().date().isoformat()
        location = "data/csv"
        Path(location).mkdir(parents=True, exist_ok=True)

        self.filename = f"{spider.name}-{scraping_date}.csv"
        self.file = open(f"{location}/{self.filename}", "w+b")
        self.exporter = CsvItemExporter(self.file)
        self.exporter.start_exporting()

    def spider_closed(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        item_data = {}
        for key, value in ItemAdapter(item).asdict().items():
            if isinstance(value, str):
                value = value.replace("\n", " ").strip()
            item_data[key] = value
        self.exporter.export_item(item_data)
        return item


class JSONPipeline:
    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
        crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
        return pipeline

    def spider_opened(self, spider):
        scraping_date = datetime.utcnow().date().isoformat()
        location = "data/json"
        Path(location).mkdir(parents=True, exist_ok=True)

        self.filename = f"{spider.name}-{scraping_date}.json"
        self.file = open(f"{location}/{self.filename}", "w", encoding="utf-8")
        header = "[\n"
        self.file.write(header)

    def spider_closed(self, spider):
        footer = "]\n"
        self.file.write(footer)
        self.file.close()

        with open(f"data/json/{self.filename}", "r", encoding="utf-8") as reader:
            data = reader.read()

        data = data.rpartition(",")
        data = data[0] + data[-1]
        data = json.loads(data)
        with open(f"data/json/{self.filename}", "w", encoding="utf-8") as writer:
            writer.write(json.dumps(data, indent=4, ensure_ascii=False))

    def process_item(self, item, spider):
        data = ItemAdapter(item).asdict()
        line = json.dumps(data, indent=4, ensure_ascii=False) + ",\n"
        self.file.write(line)
        return item


class JSONLinesPipeline:
    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
        crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
        return pipeline

    def spider_opened(self, spider):
        scraping_date = datetime.utcnow().date().isoformat()
        location = f"data/jsonline/{scraping_date}"
        Path(location).mkdir(parents=True, exist_ok=True)

        self.product_information_filename = "product-info.jl"
        self.product_information_file = open(f"{location}/{self.product_information_filename}", "w", encoding="utf-8")

        self.product_coordinates_filename = "product-coordinates.jl"
        self.product_coordinates_file = open(f"{location}/{self.product_coordinates_filename}", "w", encoding="utf-8")

        self.product_size_filename = "product-sizes.jl"
        self.product_size_file = open(f"{location}/{self.product_size_filename}", "w", encoding="utf-8")

        self.product_technology_filename = "product-technology.jl"
        self.product_technology_file = open(f"{location}/{self.product_technology_filename}", "w", encoding="utf-8")

        self.product_review_filename = "product-review.jl"
        self.product_review_file = open(f"{location}/{self.product_review_filename}", "w", encoding="utf-8")

    def spider_closed(self, spider):
        self.product_information_file.close()
        self.product_coordinates_file.close()
        self.product_size_file.close()
        self.product_technology_file.close()
        self.product_review_file.close()

    def process_item(self, item, spider):
        product = ItemAdapter(item).asdict()

        product_information = process_single_product(product)
        product_information = json.dumps(product_information, ensure_ascii=False) + "\n"
        self.product_information_file.write(product_information)

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

        return item


class MongoDBPipeline:
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get("MONGO_URI"),
            mongo_db=crawler.settings.get("MONGO_DATABASE", "adidas"),
        )

    def open_spider(self, spider):
        self.client = MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        data = ItemAdapter(item).asdict()
        data["scraped_on"] = datetime.combine(datetime.utcnow().date(), datetime.min.time())
        self.db[spider.name].insert_one(data)
        return item
