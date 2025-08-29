from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from io import BytesIO
import datetime

def create_pdf_report(data):
    """Generates a PDF report from assessment data without WeasyPrint (uses ReportLab)."""
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # --- Title ---
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, height - 50, "Shell Shield Risk Report")

    # --- Date ---
    generation_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 70, f"Generated on: {generation_date}")

    # --- Report Content ---
    c.setFont("Helvetica", 12)
    y = height - 120
    for key, value in data.items():
        line = f"{key}: {value}"
        c.drawString(50, y, line)
        y -= 20
        if y < 50:  # New page if space runs out
            c.showPage()
            c.setFont("Helvetica", 12)
            y = height - 50

    # --- Finalize PDF ---
    c.showPage()
    c.save()
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
