import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Union

from typer import Typer

from adidas.email import send_email

app = Typer()


@app.command(name="run")
def run_spider(limit: Union[int, None] = None, mail_on_finish: bool = False):
    current_date = datetime.now().date().isoformat()
    location = f"data/logs/{current_date}"
    Path(location).mkdir(parents=True, exist_ok=True)

    version = len([file for file in Path(location).glob("*") if file.is_file()])
    if version:
        current_latest_version = Path(f"{location}/latest.log")
        renamed_file = Path(f"{location}/version-{version}.log")
        current_latest_version.rename(renamed_file)

    command = "scrapy crawl products"
    if limit:
        command = f"{command} -a limit={limit}"

    try:
        subprocess.run(f"{command} 2>&1 | tee {location}/latest.log", shell=True)
    except Exception:
        subprocess.run(f"{command}", shell=True)
    finally:
        if mail_on_finish:
            send_email(subject="Completion of Scraper Task")


@app.command(name="clean")
def clean_slate():
    ack = input("This is a destructive operation. Yes to continue, Ctrl+C to cancel: ")
    if ack.lower() == "yes":
        try:
            directory_path = Path("./data")
            shutil.rmtree(directory_path)
        except Exception:
            print("Nothing to clean up.")


@app.command(name="report")
def manual_report():
    send_email(subject="Completion of Scraper Task")


if __name__ == "__main__":
    app()
