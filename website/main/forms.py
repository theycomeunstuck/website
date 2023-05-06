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


class LoginUserForm():
    def is_valid(self, POST):
        email = POST.get('email')
        password = POST.get('password')
        print(email, password)
        if email != "" and password != "":
            try:
                user = auth.sign_in_with_email_and_password(email, password)
                return True
            except Exception as e:
                error_json = e.args[1]
                error = json.loads(error_json)['error']['message']
                if error == "EMAIL_NOT_FOUND":
                    error = "Пользователь с такой почтой не найден"
                elif error == "INVALID_PASSWORD":
                    error = "Неверный пароль"
                print(error)
                return error
        else:
            return ""

    def auth(self, POST):
        email = POST.get('email')
        password = POST.get('password')
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            json_user = db.child('users').child(user['localId']).child('profile').get()
            # user_data = json_user.val()
            return user

        except Exception as e:
            print(e)

    def fill_fields(self, localId):
        student = db.child('users').child(localId).child('profile').get(0)

        data = student.val()
        return data['name'], data['surname'], data['letter'], data['class'], data['countAchievements']
