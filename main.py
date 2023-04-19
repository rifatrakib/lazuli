import subprocess

if __name__ == "__main__":
    try:
        subprocess.run("scrapy crawl products 2>&1 | tee records.log", shell=True)
    except Exception:
        subprocess.run("scrapy crawl products")
