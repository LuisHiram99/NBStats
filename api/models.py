from django.db import models

# Create your models here.

class Conference(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Division(models.Model):
    name = models.CharField(max_length=50)
    conference = models.ForeignKey(Conference, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    
class Team(models.Model):
    team_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    abbreviation = models.CharField(max_length=5)
    nickname = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50, null=True, blank=True)
    year_founded = models.IntegerField(null=True, blank=True)

    division = models.ForeignKey(Division, on_delete=models.SET_NULL, null=True)
    conference = models.ForeignKey(Conference, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name
    
class Season(models.Model):
    year = models.IntegerField(primary_key=True)
    start_date = models.DateField(null= True, blank=True)
    end_date = models.DateField(null = True, blank=True)
    is_current = models.BooleanField(default=False)

    def __str__(self):
        return str(self.year)

class Player(models.Model):
    player_id = models.IntegerField(primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    full_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    #Physical Attributes
    height = models.FloatField(null=True, blank=True) # Format = 6-2"
    weight = models.FloatField(null=True, blank=True) # In pounds 
    date_of_birth = models.DateField(null=True, blank=True)

    #Draft into
    draft_year = models.IntegerField(max_length=4, null=True, blank=True)
    draft_round = models.IntegerField(max_length=2, null=True, blank=True)
    draft_number = models.IntegerField(null=True, blank=True)

    #Current team
    current_team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True)

    #Bio
    country = models.CharField(max_length=50, null=True, blank=True)
    college = models.CharField(max_length=100, null=True, blank=True)

    profile_url = models.URLField(max_length=200, null=True, blank=True)


    def __str__(self):
        return self.full_name
