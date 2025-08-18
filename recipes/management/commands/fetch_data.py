from django.core.management.base import BaseCommand
from recipes.tasks import fetch_recipes

class Command(BaseCommand):
    help = 'Feych recipes from Spoonacular'

    def handle(self, *args, **options):
        result = fetch_recipes.delay()
        self.stdout.write(f'Task started: {result.id}')
