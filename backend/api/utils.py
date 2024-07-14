import io
import os

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

from foodgram.constants import (
    FONT_SIZE_HEADER,
    FONT_SIZE_INGREDIENTS,
    INDENT_TOP_REGULAR,
    INDENT_LEFT_REGULAR,
    INDENT_AFTER_HEADER,
    INDENT_BETWEEN_INGREDIENTS
)


def generate_pdf(ingredients):
    """Создает из списка ингредиентов файл pdf с поддержкой кириллицы."""
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    _, height = letter

    current_dir = os.path.dirname(__file__)
    font_path = os.path.join(current_dir, "fonts/dejavusans.ttf")

    pdfmetrics.registerFont(TTFont("DejaVuSans", font_path))
    pdf.setFont("DejaVuSans", FONT_SIZE_HEADER)
    position_vertical = height - INDENT_TOP_REGULAR

    pdf.drawString(
        INDENT_LEFT_REGULAR, position_vertical, "Ваш список покупок:"
    )
    position_vertical -= INDENT_AFTER_HEADER

    pdf.setFont("DejaVuSans", FONT_SIZE_INGREDIENTS)

    for ingredient in ingredients:
        name = ingredient.get("name")
        measurement = ingredient.get("measurement")
        amount = ingredient.get("amount")
        pdf.drawString(
            INDENT_LEFT_REGULAR,
            position_vertical,
            f"{name}: {amount} {measurement}"
        )
        position_vertical -= INDENT_BETWEEN_INGREDIENTS
        if position_vertical < INDENT_TOP_REGULAR:
            pdf.showPage()
            position_vertical = height - INDENT_TOP_REGULAR

    pdf.save()
    buffer.seek(0)
    return buffer
