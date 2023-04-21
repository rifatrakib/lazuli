import json
import sys
from datetime import datetime
from pathlib import Path

from scrapy import signals


class AdidasSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.
        scraping_date = datetime.now().date().isoformat()
        location = f"data/dashboard/{scraping_date}"

        if response.status == 200:
            with open(f"{location}/latest.jl", "a", encoding="utf-8") as writer:
                writer.write(
                    json.dumps(
                        {
                            "url": response.url,
                            "sent_at": response.headers["request_sent"].decode("utf-8"),
                            "received_at": response.headers["response_received"].decode("utf-8"),
                            "response_size": sys.getsizeof(response.body),
                        }
                    )
                )
                writer.write("\n")

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)

        scraping_date = datetime.now().date().isoformat()
        location = f"data/dashboard/{scraping_date}"
        Path(location).mkdir(parents=True, exist_ok=True)

        version = len([file for file in Path(location).glob("*") if file.is_file()])

        if version:
            current_latest_version = Path(f"{location}/latest.jl")
            renamed_file = Path(f"{location}/version-{version}.jl")
            current_latest_version.rename(renamed_file)


class AdidasDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.
        request.headers["request_sent"] = datetime.now().isoformat()

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.
        response.headers["request_sent"] = request.headers["request_sent"]
        response.headers["response_received"] = datetime.utcnow().isoformat()

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)
