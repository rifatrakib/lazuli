import json
import subprocess

from services.etl import (
    prepare_product_coordinates,
    prepare_product_reviews,
    prepare_product_sizes,
    prepare_products,
    process_special_functions,
)

if __name__ == "__main__":
    try:
        subprocess.run("scrapy crawl products 2&>1 | tee records.log", shell=True)
    except Exception:
        subprocess.run("scrapy crawl products")

    with open("data/json/products-2023-04-19.json", encoding="utf-8") as reader:
        products = json.loads(reader.read())

    prepare_products(products)
    prepare_product_coordinates(products)
    prepare_product_sizes(products)
    process_special_functions(products)
    prepare_product_reviews(products)
