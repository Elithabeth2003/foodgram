import json
from django.core.management.base import BaseCommand
from recipes.models import Tag


class Command(BaseCommand):
    help = 'Импорт тегов из data/tags.json'

    def handle(self, *args, **kwargs):
        with open(
            'D:/Dev/foodgram/data/tags.json', 'r', encoding='utf-8'
        ) as file:
            data = json.load(file)

        tags = [
            Tag(name=item['name'], slug=item['slug'])
            for item in data
        ]
        Tag.objects.bulk_create(tags, ignore_conflicts=True)
        self.stdout.write(self.style.SUCCESS('Успешно импортированы теги'))
