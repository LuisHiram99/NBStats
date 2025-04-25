import json
import django.core.management.base import BaseCommand
from api.models import TeamStats

class Command(BaseComand):
    help = 'Import JSON data into the database'

    def handle(self,*args,**kwargs):
        with open(r"/Users/luishernandez/Desktop/NBStats/libretas/lakers_stats.json", "r", encoding="utf8") as file:
            data = json.load(file)
            print(data)