import csv

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


CSV_DIR = 'D:/Dev/foodgram/data/'


class Command(BaseCommand):
    help = 'Import CSV Data into Django Models'

    def import_model(self, file_path, model):
        """Импорт данных из CSV файла в модель."""
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                name, measurement_unit = row
                Ingredient.objects.create(
                    name=name, measurement_unit=measurement_unit
                )

    def handle(self, *args, **options):
        files_model = {
            'ingredients.csv': Ingredient,
        }
        for file_name, model in files_model.items():
            file_path = CSV_DIR + file_name
            self.import_model(file_path, model)

        self.stdout.write(self.style.SUCCESS('Данные добавлены'))
