import json, time, base64, datetime, pytz
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_protect
from django.core.files.base import ContentFile
from . import models
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User, UserManager
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.hashers import PBKDF2PasswordHasher as hasher
from django.views.generic import ListView
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def check_group_pass(request, group_id):
	try:
		gamer = models.Gamer.objects.get(user=request.user)
		return redirect('game', team_id=group_id)
	except:
		password = request.GET.get('password')
		my_team = models.Team.objects.get(pk=group_id)
		if(my_team.team_pass == password):
			gamer = models.Gamer(team = my_team, user=request.user)
			gamer.save()
			return redirect('game', team_id=group_id)
		messages.add_message(request, messages.ERROR, 'Неправильный пароль!')
		return redirect('home')



@login_required
def moderatorDetail(request, answer_id):
	answer = models.AnswerToCheck.objects.get(pk=answer_id)
	if(request.method == "POST"):
		good = request.POST.get('good')
		bad = request.POST.get('bad')
		if(good == "Good!"):
			answer.is_right = True
			answer.save()
			return redirect('my_admin')
		elif(bad == "Bad!"):
			msg = request.POST.get('comment')
			messages.add_message(request, messages.ERROR, msg)
			answer.is_right = False
			answer.save()
			return redirect('my_admin')
		else:
			return redirect('my_admin')
		return HttpResponse(good)
	
	return render(request, 'game1/answerDetail.html', {'answer':answer})


class ModeratorView(View, LoginRequiredMixin):
	login_url = 'login'
	def get(self, request):
		answerToCheck = models.AnswerToCheck.objects.all()
		if(request.user.is_staff and request.user.is_superuser):
			return render(request, 'game1/admin_panel.html', {'answers':answerToCheck})
		else:
			messages.add_message(request, messages.ERROR, 'You are not admin!')
			return redirect('home')


@login_required
def TeamList(request):
	try:
		gamer = get_object_or_404(models.Gamer, user=request.user)
		return redirect('game', team_id=gamer.team.id)
	except:

		teams = models.Team.objects.all()
		return render(request ,'game1/home_page.html', {'object_context':teams})

@login_required
def game_page(request, team_id):
	#TODO
	#*Check if time isnt expired

	#Check if user is a gamer
	try:
		gamer = models.Gamer.objects.get(user=request.user)
	except:
		messages.add_message(request, messages.ERROR, "You are not a gamer!")
		return redirect('home')

	if(gamer):
		my_boy = models.Gamer.objects.get(user=request.user)
		#check if user not from another team
		if(my_boy.team.id == team_id):
			my_team = models.Team.objects.get(pk=team_id)
			start_time = my_team.start
			finish_time = my_team.finish.isoformat()
			#Check if time is expired
			now = datetime.datetime.now()
			now = pytz.utc.localize(now)
			deadline = pytz.utc.localize(my_team.finish)
			if(deadline < now):
				return HttpResponse("Time is expired!")
			#Then get mission
			try:
				my_mission = models.Mission.objects.get(step=my_team.progress)
				place_photo = my_mission.img.url
			except:
				#If mission isnt exist, then show message
				
				return redirect('finish')

			return render(request, 'game1/game_page.html', {'mission_id':my_team.progress, 'finish': finish_time, 'photo':place_photo})
		#user is not from this team	
		else:
			messages.add_message(request, messages.ERROR, 'You are not from this team!')
			return redirect('home')
	#User isnt Gamer, so, we ll check pass of group and make it for us
	else:
		#check pass group
		gamer = models.Gamer(user=request.user, team=models.Team.objects.get(id=team_id))
		gamer.save()

def finish(request):
	return render(request, 'game1/finish.html', {})


@login_required
def get_answer(request):
	#

	#Receive images in json, base64, jpeg
	print(request.body.decode())
	received_json_data = json.loads(request.body.decode())
	#Selfie img
	format, selfie_img = received_json_data['Answers']['selfie'].split(';base64,') 
	ext = format.split('/')[-1] 
	selfie = ContentFile(base64.b64decode(selfie_img), name='temp.' + ext)
	#Place img
	format, place_img = received_json_data['Answers']['place'].split(';base64,') 
	ext = format.split('/')[-1] 
	place = ContentFile(base64.b64decode(place_img), name='temp.' + ext)
	#Save img to admin panel, that after will be checked by moderator
	gamer = models.Gamer.objects.get(user=request.user)
	team = gamer.team
	answerToCheck = models.AnswerToCheck(selfie=selfie, place=place, step=team.progress, team=team)
	answerToCheck.save()
	
	#Check if answer is True or false, by updating the statement of answer
	while(models.AnswerToCheck.objects.get(pk=answerToCheck.pk).check_answer() == None ):
		#time.sleep(3) to unfreeze server
		time.sleep(3)
		continue
	data_to_send = ""

	if(models.AnswerToCheck.objects.get(pk=answerToCheck.pk).check_answer() == True):
		team_to_update = models.Team.objects.get(pk=team.pk)
		team_to_update.progress = team.progress+1
		team_to_update.save()
	else:
		pass

	return HttpResponse(models.AnswerToCheck.objects.get(pk=answerToCheck.pk).check_answer())


def signup(request):
	if(request.user.is_authenticated):
		return redirect('home')

	if(request.method == "POST"):
		username = request.POST.get('username')
		email = request.POST.get('email')
		password = request.POST.get('password')
		password1 = request.POST.get('password1')
		if(password != password1):
			messages.add_message(request, messages.ERROR, 'Passwords are not equals')
			return redirect('signup')
		try:
			user = get_object_or_404(models.User, username=username)
			my_mail = get_object_or_404(models.User, email=email)
			# existed_email = get_object_or_404(models.User, email=email)
			if(user or my_mail):
				messages.add_message(request, messages.ERROR, 'This user already exists!')
				return redirect('signup')
		except:
			user = User.objects.create_user(username, email, password)
			user.save()
			login(request, user)
			return redirect('home')
	
	return render(request, 'game1/signup.html')



