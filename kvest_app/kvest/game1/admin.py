from django.contrib import admin
from .models import Team, Mission, Gamer, AnswerToCheck, Key
# Register your models here.

class MissionAdmin(admin.ModelAdmin):
	list_display = ('name', 'step', 'team_name')

admin.site.register(Team)
admin.site.register(Mission, MissionAdmin)
admin.site.register(Gamer)
admin.site.register(AnswerToCheck)
admin.site.register(Key)

