import os
import shutil
import subprocess
import zipfile
from pathlib import Path
from typing import Union

from typer import Typer

from adidas.email import send_email
from adidas.reporter import create_dashboard
from adidas.utils import create_directory

app = Typer()


@app.command(name="run")
def run_spider(limit: Union[int, None] = None, create_viz: bool = False, mail_on_finish: bool = False):
    location = create_directory("data/logs", "log")
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
        if create_viz:
            create_dashboard()


@app.command(name="clean")
def clean_slate(backup: bool = False):
    ack = input("This is a destructive operation. Yes to continue, Ctrl+C to cancel: ")
    if ack.lower() == "yes":
        try:
            if backup:
                location = create_directory("./archive", "zip")
                with zipfile.ZipFile(f"{location}/latest.zip", "w", zipfile.ZIP_DEFLATED) as zipf:
                    for root, dirs, files in os.walk("./data"):
                        for file in files:
                            zipf.write(os.path.join(root, file))

            directory_path = Path("./data")
            shutil.rmtree(directory_path)
        except Exception:
            print("Nothing to clean up.")


@app.command(name="dashboard")
def latest_dashboard(save: bool = False):
    create_dashboard(save)


@app.command(name="report")
def manual_report():
    send_email(subject="Completion of Scraper Task")


if __name__ == "__main__":
    app()
