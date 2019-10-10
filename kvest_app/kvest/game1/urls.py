from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static 
from django.conf import settings # new

urlpatterns = [
	path('', views.TeamList, name='home'),
	path('game/<int:team_id>', views.game_page, name='game'),
	path('post_answer', views.post_answer),
        path('check_answer', views.check_answer),
	path('accounts', include("django.contrib.auth.urls")),
	path('accounts/login', auth_views.LoginView.as_view(template_name='game1/login.html'), name='login'),
	path('accounts/login/', auth_views.LoginView.as_view(template_name='game1/login.html'), name='login'),
	path('accounts/signup', views.signup, name="signup"),
	path('game/admin', views.ModeratorView.as_view(), name='my_admin'),
	path('game/admin/<int:answer_id>', views.moderatorDetail, name='answerDetail'),
	path('check_group_pass/<int:group_id>', views.check_group_pass, name='check_group_pass'),
	path('finish', views.finish, name='finish')
]

if settings.DEBUG: # new
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
