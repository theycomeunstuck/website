from django import forms
import pyrebase, urllib3, json
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError



firebaseConfig = {
    'apiKey': "AIzaSyCtqWOd1gcXuDH3cFUdQzxj8Ii6f4f9zS4",
    'authDomain': "authstudent2.firebaseapp.com",
    'databaseURL': "https://authstudent2.firebaseio.com",
    'projectId': "authstudent2",
    'storageBucket': "authstudent2.appspot.com",
    'messagingSenderId': "1087868700511",
    'appId': "1:1087868700511:web:f869ca3561ab845c5418ea",
    'measurementId': "G-XP68GE315L"
}
firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
db = firebase.database()
storage = firebase.storage()


class LoginUserForm():
    def is_valid(self, POST):
        email = POST.get('email')
        password = POST.get('password')
        if email != "" and password != "":
            try:
                print("forms.py (32) получение user -- авторизациЯ")
                user = auth.sign_in_with_email_and_password(email, password)
                return True
            except Exception as e:
                error_json = e.args[1]
                error = json.loads(error_json)['error']['message']
                if error == "EMAIL_NOT_FOUND":
                    error = "Пользователь с такой почтой не найден"
                elif error == "INVALID_PASSWORD":
                    error = "Неверный пароль"
                print(f"forms.py (41)\n{error}")
                return error
        else:
            return ""

    def auth(self, POST):
        email = POST.get('email')
        password = POST.get('password')
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            # user_data = json_user.val()
            return user

        except Exception as e:
            print(e)

    def fill_fields(self, localId):
        student = db.child('users').child(localId).child('profile').get()
        data = student.val()

        _Data = db.child('users').child(localId).child('achievements').get().val()
        i = 0

        for _key in _Data:
            i += 1

        data['countAchievements'] = i
        return data['name'], data['surname'], data['letter'], data['class'], data['countAchievements']


def does_user_auth(request):  # request.COOKIES
    if len(request.COOKIES) != 3 or len(request.COOKIES) < 3 or request.COOKIES == '{}':
        print(f'forms.py | 67 | redirect to auth')
        return 'auth'
    # try:
    #     if not(request.COOKIES['user_localId'] in request.COOKIES) and not(request.COOKIES['user_idToken'] in request.COOKIES):
    #         print(f'forms.py | 71 | redirect to auth')
    #         return 'auth'
    #
    # except Exception as e:
    #     print(f"forms.py | 74| {e}")
        # idToken = request.COOKIES['user_idToken']
        # try:
        #     if request.COOKIES["csrftoken"] != "" and request.COOKIES["csrftoken"] != "" and request.COOKIES["csrftoken"] != "":
        #         continue
        #     else:
        #         redirect("auth")
        # except Exception as e:
        #     print(f"error when check cookie| {e} \nviews.py (81)")
        #     return redirect("auth")
        # TODO | если пользователь не авторизован, то надо и даже не пытаться выводить ему имя и фамку, но постоянно
        # проверять пользователя -- тоже гемор и долго (наверное). но пока что изложеннное выше решение


def add_user_achievement(request):
    try:
        localId = request.COOKIES['user_localId']
        idToken = request.COOKIES['user_idToken']

        #добавление достижения в бд
        _File = request.FILES['scan']
        competition_name, _File_format, _Date = request.POST.get('workName'), str(_File).split(".")[-1], request.POST.get('eventDate')
        _Year, _Month, _Day = _Date.split("-")
        _Date = f'{_Day}.{_Month}.{_Year}'
        achievement = {"competition_type": request.POST.get('competitionType'),
                       "competition_name": competition_name,
                       "work_type": request.POST.get('workType'),
                       "type_document": request.POST.get('documentType'),
                       "date": _Date,
                       "place": request.POST.get('position'),
                       "level_competition": request.POST.get('olympiadLevel'),
                       "subject": request.POST.get('subject'),
                       'file_format': _File_format}


        db.child('users').child(localId).child('achievements').push(achievement)

        #добавление скана в бд (storage)
        achievements = db.child('users').child(localId).child('achievements').get()
        data3 = achievements.val()

        for key in data3:
            name2 = data3[key]['competition_name']
            if name2.lower() == competition_name.lower():
                storage.child("/" + localId + "/" + key + "." + _File_format).put(_File, idToken)
                break
        return 'Достижение успешно добавлено!'
    except Exception as e:
        print(f'forms.py| 121| !!!достижение НЕ добавлено\n{e}')
        return f'Достижение не добавлено.\n{e}'

    # storage.child("/" + localId + "/" + key_achievement + "." + _File_format).put(_File, idToken)

