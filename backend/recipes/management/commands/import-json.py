import json

from django.core.management.base import BaseCommand
from recipes.models import Ingredient


JSON_DIR = 'D:/Dev/foodgram/data/'


class Command(BaseCommand):
    help = 'Import JSON Data into Django Models'

    def import_model(self, file_path, model):
        """Импорт данных из JSON файла в модель."""
        with open(file_path, encoding='utf-8') as jsonfile:
            data = json.load(jsonfile)
            for item in data:
                name = item.get('name')
                measurement_unit = item.get('measurement_unit')
                model.objects.create(
                    name=name, measurement_unit=measurement_unit
                )

    def handle(self, *args, **options):
        files_model = {
            'ingredients.json': Ingredient,
        }
        for file_name, model in files_model.items():
            file_path = JSON_DIR + file_name
            self.import_model(file_path, model)

        self.stdout.write(self.style.SUCCESS('Данные добавлены'))
