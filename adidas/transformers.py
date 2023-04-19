from datetime import datetime
from pathlib import Path

import pandas as pd


def generate_product_spreadsheet():
    current_date = datetime.utcnow().date().isoformat()
    destination = "data/spreadsheets"
    Path(destination).mkdir(parents=True, exist_ok=True)
    writer = pd.ExcelWriter(f"{destination}/{current_date}.xlsx", engine="openpyxl")

    sheets = {
        "product-information": "Product Information",
        "product-coordinates": "Coordinated Products",
        "product-sizes": "Sizes",
        "product-technologies": "Technologies",
        "product-reviews": "Reviews",
    }

    for filename, sheet_name in sheets.items():
        source = f"data/jsonlines/{current_date}/{filename}.jl"
        df = pd.read_json(source, lines=True)
        df.to_excel(writer, sheet_name=sheet_name, index=False)

    writer.close()
