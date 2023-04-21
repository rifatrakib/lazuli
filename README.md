# lazuli

### Project Introduction

This project aims to develop a comprehensive and efficient web scraping tool that collects and preprocesses data from the Japanese Adidas website. The scraper is built using Scrapy, a popular web crawling framework in Python, and Pydantic, a library for data validation and settings management, to preprocess the data. The processed data is then stored as JSONL files using pipelines, and converted into well-formatted Excel spreadsheets using Pandas and Openpyxl.

In addition to these features, the scraper provides several other options, including the ability to automatically send email confirmations containing key performance indicators (KPIs) about the scraping session, generate and save dashboards as PNG files using Matplotlib and Seaborn, and support for versioning of collected data, processed data, logs, scraper performance statistics, and generated dashboards. The CLI app built using Typer makes it easy to navigate through all these features and more.

The scraper utilizes Scrapy's downloader and spider middleware features to capture data during the request-response cycle, which are then used to build the dashboard. The dashboard provides valuable insights into the scraping process, such as the number of requests made, amount of bytes received as responses (Network In) per second, and average download rate over the scraping session. These information can help identify the best configuration for Scrapy that can optimize and boost performance.

The project's overall goal is to provide a reliable and efficient web scraping tool for data analysts and researchers. It aims to streamline the data collection and preprocessing process, allowing users to quickly and easily obtain relevant data from the Japanese Adidas website. The project's modular design makes it easy to customize and extend, making it a versatile tool for a wide range of use cases.


### Features

This project comes with the following features:

* Scrapy web crawler.

* Fully automated data preprocessing & validation, ETL (Extract Transform Load), and data modeling workloads.

* Versioning system (for preprocessed & final reports along with other important things like logs for monitoring purposes and scraping session statistics).

* Fully automated reporting tools (email session reports with KPIs) and visualization (viewing and saving graphs to provide visualization about KPIs and insights about scraping session performance).

* typer CLI application to provide central management of all the features.


### How to use?

1. First, clone the "rifatrakib/lazuli" repository from GitHub and navigate into the directory:

```
git clone https://github.com/rifatrakib/lazuli.git
cd lazuli
```

2. Install the required dependencies using `poetry`:

```
pip install poetry
poetry install
```

if you are having trouble using these commands, then just use `pip`:

```
pip install -r requirements.txt
```

3. To use the automated email features, you will need a `.env` file containing 4 variables as provided in the `.env.sample`.

4. The `main.py` comes with a CLI app built using `typer`.

    (a) To run the scraper, run:

    ```
    python main.py run
    ```

    optionally, you can limit the number of products you want to scrape (for example, this command collects 300 products):

    ```
    python main.py run --limit 300
    ```

    optionally, you can send reports about scraping session including the processed spreadsheet automatically via email (REQUIRED: configuration variables in the `.env` file):

    ```
    python main.py run --mail-on-finish
    ```

    optionally, you can generate reports on scraper performance:

    ```
    python main.py run --create-viz
    ```

    All these options are optional, you can mix and match as you like. When the limit option is not provided, all the data will be scraped.

    (b) To delete all historical data:

    ```
    python main.py clean
    ```

    optionally, you can archive all the historical data:

    ```
    python main.py clean --backup
    ```

    (c) To visualize the latest scraping session performance:

    ```
    python main.py dashboard
    ```

    optionally, you can save newly rendered graph:

    ```
    python main.py dashboard --save
    ```

    (d) To email the scraping report of the last scraping session with the processed and formatted spreadsheet attached:

    ```
    python main.py report
    ```


### The reason behind choosing Scrapy

This project was built using Scrapy for several reasons.

Firstly, Scrapy's asynchronous networking allows for handling multiple requests concurrently, resulting in faster data extraction compared to browser automation tools like Selenium or Playwright. Browser automation tools use a full-blown web browser to navigate to web pages and perform scraping tasks, which can be much slower and consume more resources.

Secondly, Scrapy only requests the HTML content of a web page or a particular API endpoint in most cases, reducing the amount of network bandwidth used and making the scraping process faster and more efficient. Additionally, Scrapy provides built-in support for handling cookies, managing sessions, and handling redirections, making it easier to handle common web scraping tasks.

Lastly, Scrapy's robust fault tolerance and flexible crawling make it a more reliable and efficient option for web scraping compared to lighter HTTP client packages like Requests. Scrapy provides a flexible mechanism for defining how to follow links and extract data from web pages, automatic throttling and prioritization features, and a robust system of middlewares and extensions that allow developers to customize and extend the core functionality.

Overall, Scrapy is a powerful, fault-tolerant, and flexible web scraping framework that provides a wide range of features and functionality for building scalable and robust web crawlers.


### Answer to more "Why's"

* `Why JSONLines over JSON?` - Although using JSON is almost a standard in many cases, it still has some drawbacks in this particular use case. Appending to JSON files is not good for performance in Python. This might be overlooked when the file size is small, but as the scraper continues to collect data, the file size will grow over time, and it becomes very slow. However, JSONLines format address this issue by storing a single record in each line (which themselves are valid JSON strings) and as we keep on scraping, we can just keep appending to it without any performance issue.

* `Why an additional data format in the middle`: Though it is possible to directly store the data in spreadsheets, again, it is not going to be very performant to do this kind of operation in the long run. But saving the data first in JSONLines, then using the features from `pandas` is much more performant as the package itself has dedicated support for tasks like this and it does them faster. It's also safer to keep a middle man (JSONLine records) as backup in case something goes wrong.

* `Why scrape JS?` - In my investigation and trials, I have found it to be hundreds of times faster to get the data directly from JavaScript responses instead of using something like Selenium or Playwright. For this project, I was able to pinpoint the JavaScript generated materials which could be retrieved from one of the API endpoints. This allowed me to get the data from JavaScript directly, get the HTML string from it, and then parsing it to get the necessary data. This not only did increase performace and speed by a very large margin, but also saved a large amount of bandwidth.
