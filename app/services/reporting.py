from io import BytesIO

from openpyxl import Workbook
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def build_bi_pdf_report(title: str, rows: list[tuple]) -> bytes:
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    pdf.setTitle(title)
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(40, 810, title)
    y = 780
    pdf.setFont("Helvetica", 10)
    for row in rows:
        pdf.drawString(40, y, " | ".join(str(cell) for cell in row))
        y -= 18
        if y < 60:
            pdf.showPage()
            y = 810
            pdf.setFont("Helvetica", 10)
    pdf.save()
    return buffer.getvalue()


def build_bi_xlsx_report(sheet_name: str, headers: list[str], rows: list[tuple]) -> bytes:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = sheet_name
    sheet.append(headers)
    for row in rows:
        sheet.append(list(row))

    out = BytesIO()
    workbook.save(out)
    return out.getvalue()
