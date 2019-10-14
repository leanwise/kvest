import json, time, base64, datetime, pytz
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
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
		if(models.Gamer.objects.all().filter(team = my_team).count() < 9):
			if(my_team.team_pass == password):
				gamer = models.Gamer(team = my_team, user=request.user)
				gamer.save()
				my_team.playerCount += 1
				my_team.save()
				return redirect('game', team_id=group_id)
			messages.add_message(request, messages.ERROR, 'Неправильный пароль!')
			return redirect('home')
		else:
			messages.add_message(request, messages.ERROR, "В этой команде слишком много игроков!")
			return redirect('home')

@login_required
def increment_progress(request):
	#unblock team
	team = models.Gamer.objects.get(user=request.user).team
	team.is_blocked=False
	team.save()

	received_json_data = json.loads(request.body.decode())
	print(received_json_data)
	answer = models.AnswerToCheck.objects.get(pk=received_json_data['answer_id'])
	response = ''
	if(answer.is_right == True):
		gamer = models.Gamer.objects.get(user=request.user)
		team = gamer.team
		team.progress += 1
		team.save()
		response = [{'state':'Success', 'msg': answer.comment}]
	else:
		response = [{'state': 'Failed', 'msg': answer.comment}]
	return JsonResponse(response, safe=False)


@login_required
def moderatorDetail(request, answer_id):
	answer = models.AnswerToCheck.objects.get(pk=answer_id)
	team = answer.team
	mission = models.Mission.objects.get(team=team, step=team.progress)

	if(request.method == "POST"):
		good = request.POST.get('good')
		bad = request.POST.get('bad')
		msg = request.POST.get('comment')
		if(good == "Good!"):
			answer.is_right = True
			answer.comment = msg
			answer.save()
			models.Key(team=team, value=msg).save()
			team.is_blocked = False
			team.progress += 1
			team.save()
			return redirect('my_admin')
		elif(bad == "Bad!"):
			
			answer.comment = msg
			answer.is_right = False
			answer.save()
			team.is_blocked = False
			team.save()
			return redirect('my_admin')
		else:
			return redirect('my_admin')
	
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
		object_context = {'teams':teams}
		print(object_context)
		return render(request ,'game1/home_page.html', object_context)

@login_required
def game_page(request, team_id):

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
			start_time = my_team.start.isoformat()
			finish_time = my_team.finish.isoformat()
			#Check if time is expired
			now = datetime.datetime.now()
			now = pytz.utc.localize(now)
			deadline = pytz.utc.localize(my_team.finish)
			if(deadline < now):
				return HttpResponse("Время истекло!")
			#Then get mission
			try:
				my_mission = models.Mission.objects.get(step=my_team.progress, team=my_team)
				place_photo = my_mission.img.url
			except:
				#If mission isnt exist, then show message
				
				return redirect('finish')
			answer_id = None
			if(my_team.is_blocked==True):
                            answer_id = models.Spike.objects.get(mission=my_mission).answer.pk

                        context = {}
                        context['start'] = start_time
                        context['name'] = my_mission.name
                        context['zone'] = my_mission.zone
                        context['mission_id'] = my_team.progress
                        context['finish'] = finish_time
                        context['photo'] = place_photo
                        context['is_blocked'] = my_team.is_blocked
                        context['answer_id'] = answer_id
                    return render(request, 'game1/game_page.html', context)
		#user is not from this team	
		else:
			messages.add_message(request, messages.ERROR, 'You are not from this team!')
			return redirect('home')
	else:
		#check pass group
		gamer = models.Gamer(user=request.user, team=models.Team.objects.get(id=team_id))
		gamer.save()

def finish(request):
	return render(request, 'game1/finish.html', {})


@login_required
def post_answer(request):
	#block team
	team = models.Gamer.objects.get(user=request.user).team
	if(team.is_blocked):
		print('blocked')
		return JsonResponse([{'state': 'blocked'}], safe=False)
	#Blocked first time
	


	#Receive images in json, base64, jpeg
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
	response = [{'state':'Success', 'id':answerToCheck.pk}]

	team.is_blocked=True
	team.save()
	mission = models.Mission.objects.get(step=team.progress, team=team)
	models.Spike(answer=answerToCheck, mission=mission).save()
	return JsonResponse(response, safe=False)
	

@login_required
def check_answer(request):
	received_json_data = json.loads(request.body.decode())
	print(request.body.decode())
	answer = models.AnswerToCheck.objects.get(pk=received_json_data['answer_id'])
	response = [{'state':answer.is_right}]
	if(answer.is_right != None):
		response = [{'state':answer.is_right, 'msg':answer.comment}]
	return JsonResponse(response, safe=False)



def signup(request):
	if(request.user.is_authenticated):
		return redirect('home')

	if(request.method == "POST"):
		username = request.POST.get('username')
		email = request.POST.get('email')
		password = request.POST.get('password')
		password1 = request.POST.get('password1')
		if(password != password1):
			messages.add_message(request, messages.ERROR, 'Пароли не совпадают!')
			return redirect('signup')
		try:
			user = get_object_or_404(models.User, username=username)
			
			# existed_email = get_object_or_404(models.User, email=email)
			if(user or my_mail):
				messages.add_message(request, messages.ERROR, 'Пользователь с указанными данными уже существует!')
				return redirect('signup')
		except:
			user = User.objects.create_user(username, '', password)
			user.save()
			login(request, user)
			return redirect('home')
	
	return render(request, 'game1/signup.html')


def zone(request):
	return render(request, 'game1/zone.html', {})


@login_required
def keys(request):
	try:
		gamer = models.Gamer.objects.get(user=request.user)
	except:
		return redirect('home')
	team = gamer.team
	keys = models.Key.objects.all().filter(team=team)
	return render(request, 'game1/keys.html', {'keys':keys})

def faq(request):
	return render(request, 'game1/faq.html', {})
@login_required
def check_if_blocked(request):
	team = models.Gamer.objects.get(user=request.user).team
	return JsonResponse([{'blocked':team.is_blocked}], safe=False)



