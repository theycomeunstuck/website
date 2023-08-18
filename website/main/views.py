from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, HttpResponsePermanentRedirect, JsonResponse, HttpResponseBadRequest
import pyrebase
from django.core.files.uploadedfile import UploadedFile
from django.contrib.auth.views import LoginView
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms
from django.urls import reverse_lazy, reverse
from django.db import models
from .forms import *
from .utils import *


def homepage(request):
    return HttpResponseRedirect("/authorization")
    # return render(request, "main/homepage.html")
    #todo: страница с приколами и гайд. ну типо визитная, но не визитка


# auth page
def authorization(request):
    if does_user_auth(request) == "auth":
        data = {
            'title': 'Авторизация',
        }
        returned = False

        if request.method == "POST":
            form = LoginUserForm()
            result = form.is_valid(request.POST)
            if result == True:  # если пользователь существует
                user = form.auth(request.POST)  # получаем его данные
                user_data = {
                    'localId': user['localId'],
                    'idToken': user['idToken']
                }
                response = redirect('profile')
                # response = redirect('/')
                # response.set_cookie(name='data_user', value=data, max_age=259200)
                response.set_cookie('user_localId', user_data['localId'], 259200)
                response.set_cookie('user_idToken', user_data['idToken'], 259200)
                return response
            else:

                data['error'] = result

                return render(request, "main/authorization.html", data)
        if not returned:
            return render(request, "main/authorization.html", data)
    else:
        return redirect('profile')
# !auth page end!

# profile page
def profile(request):
    # print("59 profile def | views.py")
    data = {
        'title': 'Профиль'
    }
    name_button, button_pressed = "", False

    # if request.COOKIES == '{}':
    if does_user_auth(request) == "auth":
        return redirect('auth')
    for line in request.POST:
        if "button" in line:
            button_pressed = True
            name_button = line

    if not button_pressed:
        localId = request.COOKIES['user_localId']
        data['value_name'], data['value_surname'], data['value_letter'], data['value_class'], data[
            'value_countAchievements'] = LoginUserForm().fill_fields(localId)

    else:
        profile_buttons_handler(request)

    return render(request, "main/profile.html", data)  # , data)


def profile_buttons_handler(request):
    if request.method == 'POST':
        button_name = request.POST.get('buttonName')
        if button_name == 'add_achievement':
            return redirect('add-achievement')
        elif button_name == 'list_achievements':
            return redirect('list-achievements')
        elif button_name == 'make_report':
            return redirect('make-report')
        elif button_name == '':
            pass

# !profile page end!

# add_achievement page
def add_achievement(request):
    data = {'title':'Добавление достижения'}
    if does_user_auth(request) == "auth":
        return redirect('auth')

    if request.POST.get('workName') != None :  #при редиректе метод пост
        data['message'] = add_user_achievement(request)
        if data['message'] != 'Достижение успешно добавлено!':
            data['error_message'] = data['message']
        # achievement_title = request.POST.get('achievement_title')

    return render(request, "main/add_achievement.html", data) #js script in html to redirect('profile')



# !add_achievement page end!

def list_achievements(request):
    if does_user_auth(request) == "auth":
        return redirect('auth')

    #todo: ну сделай блять симпатично css
    data = {'title': 'Список достижений', 'achievements': get_list_achievements(request)}
    return render(request, "main/list_achievements.html", data)


# !list_achievements page end!

def edit_achievement(request, key):
    if does_user_auth(request) == "auth":
        return redirect('auth')

    #todo: кнопку вернуться мб?
    url, achievement = fill_achievement_fields(request, key)

    data = {'title': 'Редактирование достижения',
            'achievement': achievement,
            'scan_url': url}

    if request.method == "POST":
        if request.POST.get('form_type') == None:
            data['message'] = edit_user_achievement(request, key)

        else:
            data['message'] = delete_user_achievement(request, key)
        print(data['message'])

        if data['message'] != 'Достижение успешно удалено!' and data['message'] != "Достижение успешно изменено!":
                data['error_message'] = data['message']

    # todo: !при скачивании имя конкурса, а не key | решение, вроде как, через скачивание на сервер, переименование, а затем пользователю файл
    # todo: !ещё бы картиночки на своём сайте показывать (в url типо), а не на клауд кидать
    # todo: * обязательно поработать над css, потому что сейчас кнопки друг на друге и при новом label вообще всё плохо!
    return render(request, "main/edit_achievement.html", data)


def make_report(request):
    #todo: сделать make_report
    print('make_report views.py')
    data = {'title': 'Формирование отчёта'}
    return render(request, "main/make_report.html", data)


def logout(request):
    response = HttpResponseRedirect("authorization")
    response.delete_cookie('user_localId')
    response.delete_cookie('user_idToken')
    return response

# todo: часть учителя
# todo: часть админа
# todo: смотри тг favorite
