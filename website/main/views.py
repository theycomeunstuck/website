from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, HttpResponsePermanentRedirect, JsonResponse
import pyrebase
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


# auth page
def authorization(request):
    print("22 views auth |views.py")
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
            # print(data)
            response = redirect('profile')
            # response = redirect('/')
            # response.set_cookie(name='data_user', value=data, max_age=259200)

            response.set_cookie('user_localId', user_data['localId'], 259200)
            response.set_cookie('user_idToken', user_data['idToken'], 259200)
            # return redirect('profile')
            return response
        else:

            data['error'] = result

            return render(request, "main/authorization.html", data)
    if not returned:
        return render(request, "main/authorization.html", data)


# !auth page end!

# profile page
def profile(request):
    # print(data)
    print("59 profile def | views.py")
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
        idToken = request.COOKIES['user_idToken']

        # fields = LoginUserForm().fill_fields(localId)
        data['value_name'], data['value_surname'], data['value_letter'], data['value_class'], data[
            'value_countAchievements'] = LoginUserForm().fill_fields(localId)


        # # print("76 data. views.py\n", data)
        # data['value_name'] = fields[0]
        # data['value_surname'] = fields[1]
        # data['value_letter'] = fields[2]
        # data['value_class'] = fields[3]
        # data['value_countAchievements'] = fields[4]
    else:
        print(91)
        profile_buttons_handler(request, name_button)

    # print(request.POST.get())
    return render(request, "main/profile.html", data)  # , data)


# def profile_buttons_handler(request, name_button):
#     if request.POST:
#         print("99")
#         if 'button_add_achievement' in request.POST:
#             add_achievements(request)
#         elif "button_list_achievements" in request.POST:
#             list_achievements(request)
#     print("something. 97 views.py")
#     return redirect("auth")
def profile_buttons_handler(request):
    if request.method == 'POST':
        button_name = request.POST.get('buttonName')
        if button_name == 'add_achievement':
            add_achievements(request)
        elif button_name == 'list_achievements':
            list_achievements(request)
        elif button_name == 'make_report':
            return JsonResponse({'redirect': reverse('report')})
    return JsonResponse({})

def add_achievements(request):
    print('add_achievement views.py')
    data = {
        'title': 'Добавление достижения'
    }
    return render(request, "main/add_achievement.html", data)


def list_achievements(request):
    print('list_achievements views.py')
    return HttpResponse("Hello | list")


def make_report(request):
    print('make_report views.py')


def logout(request):
    response = HttpResponseRedirect("authorization")  # Переадресация на страницу "auth"
    response.delete_cookie('user_localId')
    response.delete_cookie('user_idToken')
    return response

# !profile page end!
