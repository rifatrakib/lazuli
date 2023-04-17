import json

import scrapy


class ProductsSpider(scrapy.Spider):
    name = "products"
    catalogue_url_base = "https://shop.adidas.jp/f/v1/pub/product"
    product_url_base = "https://shop.adidas.jp/f/v2/web/pub/products/article"
    size_chart_url_base = "https://shop.adidas.jp/f/v1/pub/size_chart"
    reviews_url_base = "https://adidasjp.ugc.bazaarvoice.com/7896-ja_jp/<model>/reviews.djs"
    reviews_params = {
        "format": "embeddedhtml",
        "page": None,
        "productattribute_itemKcod": None,
        "scrollToTop": "true",
    }

    def start_requests(self):
        yield scrapy.Request(
            f"{self.catalogue_url_base}/list?gender=mens&limit=120&page=1",
            callback=self.parse_links,
        )

    def parse_links(self, response):
        data = response.json()

        if "canonical_param_next" in data:
            endpoint = data["canonical_param_next"].replace("item/", "list")
            yield scrapy.Request(
                f"{self.catalogue_url_base}/{endpoint}",
                callback=self.parse_links,
            )

        for product_code, information in data["articles"].items():
            yield scrapy.Request(
                f"{self.product_url_base}/{product_code}/",
                callback=self.parse_products,
                cb_kwargs=information,
            )

            yield scrapy.Request(
                f"{self.size_chart_url_base}/{information['model_code']}/",
                callback=self.parse_size_charts,
                cb_kwargs=information,
            )

            if information["review_count"] > 0:
                total_page = information["review_count"] // 10 + 1
                for page in range(1, total_page + 1):
                    self.reviews_params["page"] = page
                    self.reviews_params["productattribute_itemKcod"] = product_code
                    params = []
                    for key, value in self.reviews_params.items():
                        params.append(f"{key}={value}")

                    yield scrapy.Request(
                        f"{self.reviews_url_base}?{'&'.join(params)}",
                        callback=self.parse_reviews,
                        cb_kwargs=information,
                    )

    def parse_products(self, response, **kwargs):
        data = response.json()
        yield {**data, "product_metadata": kwargs}

    def parse_size_charts(self, response, **kwargs):
        data = response.json()
        yield {**data, "product_metadata": kwargs}

    def parse_reviews(self, response, **kwargs):
        print(response.status)
        for line in response.body.decode().split("\n"):
            if line.startswith("var materials="):
                data = line.replace("var materials=", "")[:-1]
                print(json.loads(data).keys())
                break
