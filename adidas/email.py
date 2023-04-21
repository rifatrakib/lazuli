import json
import smtplib
from datetime import datetime
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from jinja2 import Environment, FileSystemLoader

from adidas import settings

# Set up the Jinja environment and load the template
env = Environment(loader=FileSystemLoader("./templates"))


def read_stats():
    current_date = datetime.now().date().isoformat()
    location = f"data/stats/{current_date}"
    with open(f"{location}/latest.json", "r") as reader:
        stats = json.loads(reader.read())

    return {
        "finish_time": stats["finish_time"],
        "item_scraped_count": stats["item_scraped_count"],
        "elapsed_time_seconds": stats["elapsed_time_seconds"],
        "request_bytes": stats["downloader/request_bytes"],
        "response_bytes": stats["downloader/response_bytes"],
        "request_count": stats["downloader/request_count"],
        "success_count": stats["downloader/response_status_count/200"],
        "error_count": stats["downloader/request_count"] - stats["downloader/response_status_count/200"],
    }


def send_email(subject: str):
    current_date = datetime.now().date().isoformat()
    template = env.get_template("email_template.html")

    # Render the template with the context variables
    email_body = template.render(
        recipient_name=settings.RECIPIENT_NAME,
        sender_name="Adidas Scraper",
        **read_stats(),
    )

    # Set up the email message
    msg = MIMEMultipart()
    msg["From"] = settings.ADMIN_EMAIL
    msg["To"] = settings.RECIPIENT_EMAIL
    msg["Subject"] = subject

    # Attach the email body to the email message
    msg.attach(MIMEText(email_body, "html"))

    # Attach a file to the email message
    with open(f"data/spreadsheets/{current_date}/latest.xlsx", "rb") as reader:
        file_data = reader.read()
    attachment = MIMEApplication(file_data, _subtype="xlsx")
    attachment.add_header("Content-Disposition", "attachment", filename="report.xlsx")
    msg.attach(attachment)

    # Connect to the SMTP server and send the email
    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.starttls()
        smtp.login(settings.ADMIN_EMAIL, settings.ADMIN_PASSWORD)
        smtp.sendmail(settings.ADMIN_EMAIL, settings.RECIPIENT_EMAIL, msg.as_string())
