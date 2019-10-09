from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Team(models.Model):
	def __str__(self):
		return self.name

	id = models.AutoField(primary_key=True)
	name = models.CharField('Team name', max_length=100)
	progress = models.IntegerField(default=1)
	start = models.DateTimeField()
	finish = models.DateTimeField()
	team_pass = models.CharField('pass', max_length=50, default="xxxxxxxxxxxxxxxxxxxxxxxxxx1111111111111")

class Mission(models.Model):
	def __str__(self):
		return self.name
	def team_name(self):
		return self.team.name

	id = models.AutoField(primary_key=True)
	name = models.CharField('Mission name', max_length=100)
	img = models.ImageField(upload_to='mission_images/')
	zone = models.IntegerField()
	team = models.ForeignKey(Team, on_delete=models.CASCADE)
	step = models.IntegerField()

class Gamer(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	team = models.ForeignKey(Team, on_delete=models.CASCADE)


class AnswerToCheck(models.Model):
	def check_answer(self):
		return self.is_right
	selfie = models.ImageField(upload_to='selfieToCheck/')
	place = models.ImageField(upload_to='placeToCheck/')
	step = models.IntegerField()
	team = models.ForeignKey(Team, on_delete=models.CASCADE)
	is_right = models.NullBooleanField(null=True)



