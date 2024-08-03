import io
import os
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from .constants import (
    FONT_SIZE_HEADER,
    FONT_SIZE_INGREDIENTS,
    INDENT_AFTER_HEADER,
    INDENT_BETWEEN_INGREDIENTS,
    INDENT_LEFT_REGULAR,
    INDENT_TOP_REGULAR,
)
from django.utils.translation import gettext as _


def get_correct_measurement(amount, measurement):
    measurement_plural = measurement + 's'
    return _(measurement_plural)


def generate_pdf(ingredients, recipes):
    """Создает из списка ингредиентов файл pdf с поддержкой кириллицы."""
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    _, height = letter
    current_dir = os.path.dirname(__file__)
    font_path = os.path.join(current_dir, 'fonts/dejavusans.ttf')
    pdfmetrics.registerFont(TTFont('DejaVuSans', font_path))
    pdf.setFont('DejaVuSans', FONT_SIZE_HEADER)
    position_vertical = height - INDENT_TOP_REGULAR
    current_date = datetime.now().strftime('%Y-%m-%d %H:%M')
    pdf.drawString(
        INDENT_LEFT_REGULAR,
        position_vertical,
        f'Список покупок от {current_date}'
    )
    position_vertical -= INDENT_AFTER_HEADER
    pdf.setFont('DejaVuSans', FONT_SIZE_INGREDIENTS)
    for idx, recipe in enumerate(recipes, start=1):
        pdf.drawString(
            INDENT_LEFT_REGULAR, position_vertical, f'{idx}. Рецепт: {recipe}'
        )
        position_vertical -= INDENT_BETWEEN_INGREDIENTS
        if position_vertical < INDENT_TOP_REGULAR:
            pdf.showPage()
            position_vertical = height - INDENT_TOP_REGULAR
    position_vertical -= INDENT_AFTER_HEADER
    for idx, ingredient in enumerate(ingredients, start=1):
        name = ingredient.get('name').capitalize()
        measurement = ingredient.get('measurement')
        amount = ingredient.get('amount')
        correct_measurement = get_correct_measurement(amount, measurement)
        pdf.drawString(
            INDENT_LEFT_REGULAR,
            position_vertical,
            f'{idx}. {name}: {amount} {correct_measurement}'
        )
        position_vertical -= INDENT_BETWEEN_INGREDIENTS
        if position_vertical < INDENT_TOP_REGULAR:
            pdf.showPage()
            position_vertical = height - INDENT_TOP_REGULAR
    position_vertical -= INDENT_AFTER_HEADER
    pdf.setFont('DejaVuSans', FONT_SIZE_HEADER)
    pdf.drawString(
        INDENT_LEFT_REGULAR,
        position_vertical,
        'Рецепты:'
    )
    position_vertical -= INDENT_BETWEEN_INGREDIENTS
    for recipe in recipes:
        pdf.drawString(
            INDENT_LEFT_REGULAR,
            position_vertical,
            f'Рецепт: {recipe}'
        )
        position_vertical -= INDENT_BETWEEN_INGREDIENTS
        if position_vertical < INDENT_TOP_REGULAR:
            pdf.showPage()
            position_vertical = height - INDENT_TOP_REGULAR
    pdf.save()
    buffer.seek(0)
    return buffer
