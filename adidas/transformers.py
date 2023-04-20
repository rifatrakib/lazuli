# from datetime import datetime
from pathlib import Path

import pandas as pd
import pydash
from openpyxl.styles import Alignment, Border, Font, Side


def add_sheet_title(writer, sheet_name):
    worksheet = writer.sheets[sheet_name]
    cell = worksheet.cell(row=1, column=2)
    cell.value = f"{sheet_name} Table"
    cell.font = Font(color="002060", size=14, bold=True)


def format_column_headers(writer, sheet_name: str):
    worksheet = writer.sheets[sheet_name]
    worksheet.column_dimensions["A"].width = 2.71

    header_font = Font(color="002060", size=12, bold=True)
    header_alignment = Alignment(horizontal="left")
    header_border = Border(bottom=Side(border_style="medium", color="002060"))

    for col_idx, _ in enumerate(worksheet.columns):
        if col_idx == 0:
            continue

        cell = worksheet.cell(row=3, column=col_idx + 1)
        cell.value = pydash.human_case(cell.value).title()
        cell.font = header_font
        cell.alignment = header_alignment
        cell.border = header_border


def generate_product_spreadsheet():
    # current_date = datetime.utcnow().date().isoformat()
    destination = "data/spreadsheets"
    Path(destination).mkdir(parents=True, exist_ok=True)
    writer = pd.ExcelWriter(f"{destination}/2023-04-19.xlsx", engine="openpyxl")

    sheets = {
        "product-information": "Product Information",
        "product-coordinates": "Coordinated Products",
        "product-sizes": "Sizes",
        "product-technologies": "Technologies",
        "product-reviews": "Reviews",
    }

    for filename, sheet_name in sheets.items():
        source = f"data/jsonlines/2023-04-19/{filename}.jl"
        df = pd.read_json(source, lines=True)
        df.to_excel(writer, sheet_name=sheet_name, index=False, startrow=2, startcol=1)
        workbook = writer.book
        format_column_headers(writer, sheet_name)
        add_sheet_title(writer, sheet_name)
        workbook.save(f"{destination}/2023-04-19.xlsx")

    writer.close()
