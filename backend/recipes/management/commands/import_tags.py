import json

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Tag


class Command(BaseCommand):
    help = 'Импорт тегов из data/tags.json'

    def handle(self, *args, **kwargs):
        file_path = settings.BASE_DIR / 'data' / 'tags.json'
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        Tag.objects.bulk_create((
            Tag(**item) for item in data),
            ignore_conflicts=True
        )
        self.stdout.write(self.style.SUCCESS('Успешно импортированы теги'))
