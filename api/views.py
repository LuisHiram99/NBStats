from django.shortcuts import render
from .models import TeamStats
import json


def import_data(request):
    if request.method == 'POST' and request.FILES['json_file']:
        json_file = request.FILES['json_file']
        data = json.load(json_file)
        for item in data:
            team = TeamStats(
                team_id=item['TEAM_ID'],
                team_name=item['TEAM_NAME'],
                year=item['YEAR'],
                gp=item['GP'],
                wins=item['WINS'],
                losses=item['LOSSES'],
            )
            team.save()
        return render(request, 'success.html')
    return render(request, 'form.html')

# Create your views here.
