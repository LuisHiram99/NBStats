from django.contrib import admin
from .models import (
    Conference, Division, Team, Season, Player
)

@admin.register(Conference)
class ConferenceAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Division)
class DivisionAdmin(admin.ModelAdmin):
    list_display = ('name', 'conference')
    list_filter = ('conference',)

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'abbreviation', 'city', 'division', 'conference')
    list_filter = ('conference', 'division')
    search_fields = ('name', 'city', 'abbreviation')

@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ('year', 'start_date', 'end_date', 'is_current')
    list_filter = ('is_current',)

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'current_team', 'is_active')
    list_filter = ('is_active', 'current_team')
    search_fields = ('first_name', 'last_name', 'full_name')