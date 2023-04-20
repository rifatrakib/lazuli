import json
from typing import Union
from urllib.parse import parse_qs, urlparse

import scrapy
from scrapy.selector import Selector
from w3lib.html import remove_tags

from adidas.preprocessors import sanitize_size_chart_data


class ProductsSpider(scrapy.Spider):
    name = "products"
    count = 0
    in_queue = 0
    catalogue_url_base = "https://shop.adidas.jp/f/v1/pub/product"
    product_page_base = "https://shop.adidas.jp/products"
    product_api_base = "https://shop.adidas.jp/f/v2/web/pub/products/article"
    size_chart_url_base = "https://shop.adidas.jp/f/v1/pub/size_chart"
    reviews_url_base = "https://adidasjp.ugc.bazaarvoice.com/7896-ja_jp/<model>/reviews.djs"

    def __init__(self, limit: Union[int, None] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.limit = int(limit) if limit else None

    def start_requests(self):
        yield scrapy.Request(
            f"{self.catalogue_url_base}/list?gender=mens&limit=120&page=1",
            callback=self.parse_links,
        )

    def parse_links(self, response):
        data = response.json()

        if "canonical_param_next" in data and not self.limit:
            endpoint = data["canonical_param_next"].replace("item/", "list")
            yield scrapy.Request(
                f"{self.catalogue_url_base}/{endpoint}",
                callback=self.parse_links,
            )
            self.in_queue += 120
        elif "canonical_param_next" in data and self.count < self.in_queue:
            endpoint = data["canonical_param_next"].replace("item/", "list")
            yield scrapy.Request(
                f"{self.catalogue_url_base}/{endpoint}",
                callback=self.parse_links,
            )
            self.in_queue += 120

        for product_code, information in data["articles"].items():
            if self.limit and self.count >= self.limit:
                break

            yield scrapy.Request(
                f"{self.product_page_base}/{product_code}/",
                callback=self.parse_product_page,
                cb_kwargs=information,
                dont_filter=True,
            )
            self.count += 1

    def parse_product_page(self, response, **kwargs):
        product_page_url = response.url
        product_name = response.css("div.articleNameHeader.css-t1z1wj > h1::text").get()
        product_categoty = response.css("div.articleNameHeader.css-t1z1wj > a > span::text").getall()
        breadcrumb = response.css("div.breadcrumb_wrap > ul > li.breadcrumbListItem:not(.back) > a::text").getall()
        sizes = response.css("div.test-sizeSelector > ul button::text").getall()
        sense_of_fit = "適切" if response.css("span.test-marker").get() else None
        title_of_description = response.css("h4.itemFeature::text").get()
        itemization_description = []
        for item in response.css("li.articleFeaturesItem").getall():
            itemization_description.append(remove_tags(item))

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
            dont_filter=True,
        )

    def parse_product_api(self, response, **kwargs):
        data = response.json()
        yield scrapy.Request(
            f"{self.size_chart_url_base}/{kwargs['product_stat']['model_code']}/",
            callback=self.parse_size_charts,
            cb_kwargs={**kwargs, "api_info": data},
            dont_filter=True,
        )

    def parse_size_charts(self, response, **kwargs):
        data = response.json()
        data = sanitize_size_chart_data(data) if data["size_chart"] else []

        if kwargs["product_stat"]["review_count"] > 0:
            item = kwargs["product_stat"]["article"]
            model_code = kwargs["product_stat"]["model_code"]
            params = f"format=embeddedhtml&productattribute_itemKcod={item}&scrollToTop=true"
            yield scrapy.Request(
                f"{self.reviews_url_base.replace('<model>', model_code)}?{params}",
                callback=self.parse_reviews,
                cb_kwargs={**kwargs, "size_chart": data},
                dont_filter=True,
            )
        else:
            yield {**kwargs, "size_chart": data, "review_data": {}}

    def parse_reviews(self, response, **kwargs):
        review_data = {} if "review_data" not in kwargs else kwargs["review_data"]
        reviews = [] if "reviews" not in review_data else review_data["reviews"]

        for line in response.body.decode().split("\n"):
            if line.startswith("var materials="):
                review_info = json.loads(line.replace("var materials=", "")[:-1])
                review_html = Selector(text=review_info["BVRRSourceID"].replace("\\", ""), type="html")

        total_page = kwargs["product_stat"]["review_count"] // 10 + 1
        parsed_url = urlparse(response.url)
        query_params = parse_qs(parsed_url.query)
        next_page = int(query_params.get("page", ["1"])[0]) + 1

        if next_page == 2:
            rating = review_html.css(
                "#BVRRRatingOverall_ > div.BVRRRatingNormalOutOf > span.BVRRNumber.BVRRRatingNumber::text"
            ).get()
            number_of_reviews = review_html.css("span.BVRRNumber.BVRRBuyAgainTotal::text").get()
            recommended_rate = review_html.css("span.BVRRBuyAgainPercentage > span.BVRRNumber::text").get()
            sense_of_fit_rate = review_html.css(
                "div.BVRRSecondaryRatingsContainer div.BVRRRatingFit img::attr(title)"
            ).get()
            appropriation_of_length_rate = review_html.css(
                "div.BVRRSecondaryRatingsContainer div.BVRRRatingLength img::attr(title)"
            ).get()
            material_quality_rate = review_html.css(
                "div.BVRRSecondaryRatingsContainer div.BVRRRatingQuality img::attr(title)"
            ).get()
            comfort_rate = review_html.css(
                "div.BVRRSecondaryRatingsContainer div.BVRRRatingComfort img::attr(title)"
            ).get()

            review_data = {
                "rating": rating,
                "number_of_reviews": number_of_reviews,
                "recommended_rate": recommended_rate,
                "sense_of_fit_rate": sense_of_fit_rate,
                "appropriation_of_length_rate": appropriation_of_length_rate,
                "material_quality_rate": material_quality_rate,
                "comfort_rate": comfort_rate,
            }

        for review_section in review_html.css("#BVSubmissionPopupContainer"):
            review_date = review_section.css("span.BVRRReviewDate::text").get()
            review_rating = review_section.css(
                "#BVRRRatingOverall_Review_Display > div.BVRRRatingNormalImage > img::attr(title)"
            ).get()
            review_title = review_section.css("span.BVRRReviewTitle::text").get()
            review_description = review_section.css("span.BVRRReviewText::text").get()
            reviewer_id = review_section.css("span.BVRRNickname::text").get()
            reviews.append(
                {
                    "review_date": review_date,
                    "review_rating": review_rating,
                    "review_title": review_title,
                    "review_description": review_description,
                    "reviewer_id": reviewer_id,
                }
            )

        review_data["reviews"] = reviews
        if next_page <= total_page:
            item = kwargs["product_stat"]["article"]
            model_code = kwargs["product_stat"]["model_code"]
            params = f"format=embeddedhtml&page={next_page}&productattribute_itemKcod={item}&scrollToTop=true"

            yield scrapy.Request(
                f"{self.reviews_url_base.replace('<model>', model_code)}?{params}",
                callback=self.parse_reviews,
                cb_kwargs={**kwargs, "review_data": review_data},
                dont_filter=True,
            )
        else:
            yield {**kwargs, "review_data": review_data}
