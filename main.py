import shutil
import subprocess
from pathlib import Path
from typing import Union

from typer import Typer

app = Typer()


@app.command(name="run")
def run_spider(limit: Union[int, None] = None):
    command = "scrapy crawl products"
    if limit:
        command = f"{command} -a limit={limit}"

    try:
        subprocess.run(f"{command} 2>&1 | tee records.log", shell=True)
    except Exception:
        subprocess.run(f"{command}", shell=True)


@app.command(name="clean")
def clean_slate():
    ack = input("This is a destructive operation. Yes to continue, Ctrl+C to cancel: ")
    if ack.lower() == "yes":
        try:
            Path("./records.log").unlink()
            directory_path = Path("./data")
            shutil.rmtree(directory_path)
        except Exception:
            print("Nothing to clean up.")


if __name__ == "__main__":
    app()
