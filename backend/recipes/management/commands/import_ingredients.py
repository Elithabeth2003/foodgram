import os
import json
from django.core.management.base import BaseCommand
from django.conf import settings
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Импорт продуктов из data/ingredients.json'

    def handle(self, *args, **kwargs):
        base_dir = settings.BASE_DIR
        file_path = os.path.join(base_dir, 'data', 'ingredients.json')
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        ingredients = [
            Ingredient(
                name=item['name'], measurement_unit=item['measurement_unit']
            )
            for item in data
        ]
        Ingredient.objects.bulk_create(ingredients, ignore_conflicts=True)
        self.stdout.write(self.style.SUCCESS('Успешно импортированы продукты'))
