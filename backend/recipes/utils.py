import io

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

pdfmetrics.registerFont(
    TTFont("BaskervilleBoldItalic", "../fonts/BaskervilleBoldItalic.ttf")
)


def get_pdf(purchases):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)

    p.setFont("BaskervilleBoldItalic", 22)
    p.drawString(90, 800, "Foodgram. Список продуктов.")
    p.line(40, 790, 550, 790)

    p.setFont("BaskervilleBoldItalic", 18)
    x = 50
    y = 750
    if purchases:
        for i in purchases:
            string = f'{i["name"].capitalize()} - {i["total"]} {i["unit"]}'
            p.drawString(x, y, string)
            y -= 25
    else:
        p.drawString(x, y, "Список продуктов пуст.")

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer
