from django import forms
import pyrebase, firebase_admin, urllib3, json, datetime, requests
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
        #todo: проверка на то, что есть нужные куки. нет нужных куки - пока
        #todo: выход со всех других сессий, если замена пароля
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
                storage.child(f"/{localId}/{key}.{_File_format}").put(_File, idToken)
                break
        return 'Достижение успешно добавлено!'
    except Exception as e:
        print(f'forms.py| 121| !!!достижение НЕ добавлено\n{e}')
        return f'Достижение не добавлено.\n{e}'

    # storage.child("/" + localId + "/" + key_achievement + "." + _File_format).put(_File, idToken)



def get_list_achievements(request):
    #todo: если нет достижений то ченить вывести/сделать это красиво (щас слабенько и мб не работает)
    try:
        localId = request.COOKIES['user_localId']

        achievements = db.child('users').child(localId).child('achievements').get()
        _data, data = achievements.val(), {}
        if len(_data) > 0:
            for key in _data:
                name = _data[key]['competition_name']
                data[name] = key
            return data
        else:
            print("forms.py | get_list_achievements | нет достижений нечего отобразить")
            return f'У Вас нет достижений, доступных к отображению'
    except Exception as e:
        print(f'forms.py| 150| def get_list_achievements | !!!невозможно отобразить список достижений\n{e}')
        return f'Невозможно отобразить достижения.\n{e}'


def fill_achievement_fields(request, key):
    try:
        localId = request.COOKIES['user_localId']
        idToken = request.COOKIES['user_idToken']

        achievements = db.child('users').child(localId).child('achievements').child(key).get()
        data = achievements.val()

        _Day, _Month, _Year = data['date'].split(".")
        data['date'] = f'{_Year}-{_Month}-{_Day}'

        #тут имеется два метода вывода url. но, вероятно, нижний вариант лучше, если у firebase проблемки. он и используется
        # url = storage.child(f'{localId}/{key}.{data["file_format"]}').get_url(idToken)
        encoded_file_path = f'{localId}/{key}.{data["file_format"]}'.replace('/', '%2F')
        url = f'https://firebasestorage.googleapis.com/v0/b/{firebaseConfig["storageBucket"]}/o/{encoded_file_path}?alt=media'

        return url, data
    except Exception as e:
        print(f'forms.py| 145| def fill_achievement_fields | !!!невозможно  заполнить поля\n\n{e}\n\n')
        return f'Достижение не добавлено.\n{e}', ""

def edit_user_achievement(request, key):
    try:
        localId = request.COOKIES['user_localId']
        idToken = request.COOKIES['user_idToken']
        achievements = db.child('users').child(localId).child('achievements').child(key).child('file_format').get()
        data = achievements.val() #для получения формата старого файла, на случай если scan пуст

        if 'scan' in request.FILES:
            _File = request.FILES['scan']
            _File_format = str(_File).split(".")[-1]
        else:
            _File_format = data

        _Date = request.POST.get('eventDate')
        _Year, _Month, _Day = _Date.split("-")
        _Date = f'{_Day}.{_Month}.{_Year}'
        achievement = {"competition_type": request.POST.get('competitionType'),
                       "competition_name": request.POST.get('workName'),
                       "work_type": request.POST.get('workType'),
                       "type_document": request.POST.get('documentType'),
                       "date": _Date,
                       "place": request.POST.get('position'),
                       "level_competition": request.POST.get('olympiadLevel'),
                       "subject": request.POST.get('subject'),
                       'file_format': _File_format}

        if 'scan' in request.FILES:

            encoded_file_path = f'{localId}/{key}.{data}'.replace('/', '%2F')
            url = f'https://firebasestorage.googleapis.com/v0/b/{firebaseConfig["storageBucket"]}/o/{encoded_file_path}?alt=media'
            headers = {
                'Authorization': f'Bearer {idToken}',
                'Content-Type': 'application/json',
            }
            response = requests.delete(url, headers=headers)

            response.raise_for_status()
            if response.status_code == 404:
                pass
            else:
                response.raise_for_status()
            storage.child(f'/{localId}/{key}.{_File_format}').put(_File, idToken)
        db.child('users').child(localId).child('achievements').child(key).update(achievement)
        return 'Достижение успешно изменено!'

    except requests.exceptions.HTTPError as e:
        print(f'forms.py| 224| def edit_user_achievement |HTTP| !!!достижение НЕ добавлено\n{e}')
        return f'Достижение не изменено.\nПроизошла ошибка HTTP: {e}'

    except Exception as e:
        print(f'forms.py| 228| def edit_user_achievement | !!!достижение НЕ добавлено\n{e}')
        return f'Достижение не изменено.\n{e}'

def delete_user_achievement(request, key):
    try:
        localId = request.COOKIES['user_localId']
        idToken = request.COOKIES['user_idToken']
        achievements = db.child('users').child(localId).child('achievements').child(key).child('file_format').get()
        file_format = achievements.val()

        encoded_file_path = f'{localId}/{key}.{file_format}'.replace('/', '%2F')
        url = f'https://firebasestorage.googleapis.com/v0/b/{firebaseConfig["storageBucket"]}/o/{encoded_file_path}?alt=media'
        headers = {
            'Authorization': f'Bearer {idToken}',
            'Content-Type': 'application/json',
        }
        response = requests.delete(url, headers=headers)
        if response.status_code == 404:
            pass
        else:
            response.raise_for_status()
        db.child('users').child(localId).child('achievements').child(key).remove()

        return 'Достижение успешно удалено!'

    except requests.exceptions.HTTPError as e:
        print(f'forms.py| 238| def delete_user_achievement |HTTP| !!!достижение НЕ добавлено\n{e}')
        return f'Достижение не удалено.\nПроизошла ошибка HTTP: {e}'


    except Exception as e:
        print(f'forms.py| 211| def delete_user_achievement | !!!достижение НЕ добавлено\n{e}')
        return f'Достижение не удалено.\n{e}'

def validate_date(startDate, endDate):
    #если в return 2 ответа даты и даты, то ок норм а если один ответ норм а другой пуст то  шлём
    _StartYear, _StartMonth, _StartDay = map(int, startDate.split("-"))
    _EndYear, _EndMonth, _EndDay = map(int, endDate.split("-"))

    if (_StartYear, _StartMonth, _StartDay) <= (_EndYear, _EndMonth, _EndDay):
        print("Начальная дата раньше или равна конечной дате")
        return " "
    else:
        print("270 forms Начальная дата позже конечной даты")
        return None

# startDate, endDate = f'{_StartDay}.{_StartMonth}.{_StartYear}', f'{_EndDay}.{_EndMonth}.{_EndYear}'

def generate_report(request):
    pass

