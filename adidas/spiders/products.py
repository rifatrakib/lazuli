import json
from urllib.parse import parse_qs, urlparse

import scrapy


class ProductsSpider(scrapy.Spider):
    name = "products"
    catalogue_url_base = "https://shop.adidas.jp/f/v1/pub/product"
    product_page_base = "https://shop.adidas.jp/products"
    product_api_base = "https://shop.adidas.jp/f/v2/web/pub/products/article"
    size_chart_url_base = "https://shop.adidas.jp/f/v1/pub/size_chart"
    reviews_url_base = "https://adidasjp.ugc.bazaarvoice.com/7896-ja_jp/<model>/reviews.djs"

    def start_requests(self):
        yield scrapy.Request(
            f"{self.catalogue_url_base}/list?gender=mens&limit=120&page=1",
            callback=self.parse_links,
        )

    def parse_links(self, response):
        data = response.json()

        # if "canonical_param_next" in data:
        #     endpoint = data["canonical_param_next"].replace("item/", "list")
        #     yield scrapy.Request(
        #         f"{self.catalogue_url_base}/{endpoint}",
        #         callback=self.parse_links,
        #     )

        for product_code, information in data["articles"].items():
            if product_code != "HF1845":
                continue
            yield scrapy.Request(
                f"{self.product_page_base}/{product_code}/",
                callback=self.parse_product_page,
                cb_kwargs=information,
            )
            break

    def parse_product_page(self, response, **kwargs):
        product_page_url = response.url
        product_name = response.css("div.articleNameHeader.css-t1z1wj > h1::text").get()
        product_categoty = response.css("div.articleNameHeader.css-t1z1wj > a > span::text").getall()
        breadcrumb = response.css("div.breadcrumb_wrap > ul > li.breadcrumbListItem:not(.back) > a::text").getall()
        sizes = response.css("div.test-sizeSelector > ul button::text").getall()
        sense_of_fit = "適切" if response.css("span.test-marker").get() else None
        title_of_description = response.css("h4.itemFeature::text").get()
        itemization_description = response.css("li.articleFeaturesItem").getall()

        data = {
            "url": product_page_url,
            "name": product_name,
            "category": "".join(product_categoty),
            "breadcrumb": "/".join(breadcrumb),
            "available_sizes": sizes,
            "sense_of_fit": sense_of_fit,
            "title_of_description": title_of_description,
            "itemization_description": itemization_description,
        }

        yield scrapy.Request(
            f"{self.product_api_base}/{kwargs['article']}/",
            callback=self.parse_product_api,
            cb_kwargs={"product_stat": kwargs, "product_data": data},
        )

    def parse_product_api(self, response, **kwargs):
        data = response.json()
        yield scrapy.Request(
            f"{self.size_chart_url_base}/{kwargs['product_stat']['model_code']}/",
            callback=self.parse_size_charts,
            cb_kwargs={**kwargs, "api_info": data},
        )

    def parse_size_charts(self, response, **kwargs):
        data = response.json()

        if kwargs["product_stat"]["review_count"] > 0:
            model_code = kwargs["product_stat"]["article"]
            params = f"format=embeddedhtml&productattribute_itemKcod={model_code}&scrollToTop=true"
            yield scrapy.Request(
                f"{self.reviews_url_base}?{params}",
                callback=self.parse_reviews,
                cb_kwargs={**kwargs, "size_chart": data},
            )

    def parse_reviews(self, response, **kwargs):
        print(response.status, response.url)
        reviews = []

        for line in response.body.decode().split("\n"):
            if line.startswith("var materials="):
                data = line.replace("var materials=", "")[:-1]
                print(json.loads(data).keys())
                break

        total_page = kwargs["product_stat"]["review_count"] // 10 + 1
        parsed_url = urlparse(response.url)
        query_params = parse_qs(parsed_url.query)
        next_page = int(query_params.get("page", ["1"])[0]) + 1

        if next_page <= total_page:
            model_code = kwargs["product_stat"]["article"]
            params = f"format=embeddedhtml&page={next_page}&productattribute_itemKcod={model_code}&scrollToTop=true"

            yield scrapy.Request(
                f"{self.reviews_url_base}?{params}",
                callback=self.parse_reviews,
                cb_kwargs=kwargs,
            )
        else:
            yield {**kwargs, "reviews": reviews}
