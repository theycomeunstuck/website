from django import forms
import pyrebase, urllib3, json
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

# class NameForm(forms.Form):
#     email = forms.EmailField()
#     password = forms.CharField(max_length=100)

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
        student = db.child('users').child(localId).child('profile').get(0)

        data = student.val()
        return data['name'], data['surname'], data['letter'], data['class'], data['countAchievements']


def does_user_auth(request):  # request.COOKIES
    if len(request.COOKIES) != 3 or request.COOKIES == '{}':
        # return False  # пользователь не авторизован

        return 'auth'

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
    localId = request.COOKIES['user_localId']
    idToken = request.COOKIES['user_idToken']
    #добавление достижения в бд
    competition_name = request.POST.get('workName')
    achievement = {"competition_type": request.POST.get('competitionType'),
                   "competition_name": competition_name,
                   "work_type": request.POST.get('workType'),
                   "type_document": request.POST.get('documentType'),
                   "date": request.POST.get('eventDate'),
                   "place": request.POST.get('position'),
                   "level_competition": request.POST.get('olympiadLevel'),
                   "subject": request.POST.get('subject')}
    print(f'file_format: {request.POST.get("scan")}')

    db.child('users').child(localId).child('achievements').push(achievement)

    #добавление скана в бд (storage)
    # achievements = db.child('users').child(localId).child('achievements').get()
    # data3 = achievements.val()

    # for key in data3:
    #     name2 = data3[key]['competition_name']
    #     if name2 == competition_name:
    #         key_achievement = key
    # storage.child("/" + localId + "/" + key_achievement + "." + file_format).put(self.fpath, idToken)
    # print(storage.child(localId + "/" + key_achievement + "." + file_format).get_url(user['idToken']))

