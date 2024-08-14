import json

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Импорт продуктов из data/ingredients.json'

    def handle(self, *args, **kwargs):
        file_path = settings.BASE_DIR / 'data' / 'ingredients.json'
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        Ingredient.objects.bulk_create((
            Ingredient(**item) for item in data),
            ignore_conflicts=True
        )
        self.stdout.write(self.style.SUCCESS('Успешно импортированы продукты'))
