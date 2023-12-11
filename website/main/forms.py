import pyrebase, urllib3, json, datetime, requests, docx, zipfile, os
from PIL import Image
from io import BytesIO
from django import forms
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

    def user_fill_fields(self, localId):
        data = db.child('users').child(localId).child('profile').get().val()
        _Data = db.child('users').child(localId).child('achievements').get().val()
        return data['name'], data['surname'], data['letter'], data['class'], len(_Data)





def does_user_auth(request):  # request.COOKIES
    if len(request.COOKIES) != 3 or len(request.COOKIES) < 3 or request.COOKIES == '{}':
        #todo: проверка на то, что есть нужные куки. нет нужных куки - пока. | не имеет значения когда, очень простое
        #todo: выход со всех других сессий, если замена пароля | musthave, но реализуемо лишь после создания страницы с заменой пароля, простое
        return 'auth'



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

        if _File.content_type.startswith('image'):  # Проверяем, является ли файл изображением
            _File = compress_image(_File, _File_format)

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

def compress_image(image, file_format):
    print(str(image))
    img = Image.open(image)
    output = BytesIO()
    if file_format == 'jpg': file_format = 'JPEG'
    img.save(output, format=file_format, quality=70)
    output.seek(0)
    return output


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

            if _File.content_type.startswith('image'):  # Проверяем, является ли файл изображением
                _File = compress_image(_File, _File_format)
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
    try:
        localId = request.COOKIES['user_localId']
        idToken = request.COOKIES['user_idToken']

        competitionType = request.POST.getlist("competitionType") # ['Любые', 'Олимпиада'] (как массив)
        documentType = request.POST.getlist("documentType") #сертификат грамота диплом благодарность
        startDate = str(request.POST.get("startDate")).replace("-", ".")
        endDate = str(request.POST.get("endDate")).replace("-", ".")
        position = request.POST.getlist("position")
        olympiadLevel = request.POST.getlist("olympiadLevel")
        workType = request.POST.getlist("workType")
        subject = request.POST.getlist("subject")
        downloadScans = request.POST.get("downloadScans") #False == None | True = "on"
        _StartYear, _StartMonth, _StartDay = map(int, startDate.split("."))
        _EndYear, _EndMonth, _EndDay = map(int, endDate.split("."))
        _isEmpty, name, _Achievements_count, doc, paragraph = True, f'Отчёт {_StartDay}.{_StartMonth}.{_StartYear} — {_EndDay}.{_EndMonth}.{_EndYear}', 0, "", ""
        achievements = db.child("users").child(localId).child("achievements").get().val()
        startDate = datetime.datetime.strptime(startDate, "%Y.%m.%d").date()
        endDate = datetime.datetime.strptime(endDate, "%Y.%m.%d").date()

        if achievements:
            for key in achievements:
                name_comp = achievements[key]['competition_name'] #Названике работы
                type_comp = achievements[key]['competition_type'] #Вид конкурса
                level_comp = achievements[key]["level_competition"] #Уровень конкурса
                position_comp = achievements[key]["place"] #Занятое место
                subject_comp = achievements[key]["subject"] #Предметы
                workType_comp = achievements[key]["work_type"] #Вид работы (Решение задач, выступление)
                docType_comp = achievements[key]["type_document"] #Вид документа
                date = achievements[key]['date']
                if startDate <= datetime.datetime.strptime(date, "%d.%m.%Y").date() <= endDate:
                    if type_comp in competitionType or "Любые" in competitionType:
                        if workType_comp == workType or "Любые" in workType:
                            if docType_comp in documentType or "Любые" in documentType:
                                if level_comp in olympiadLevel or "Любые" in olympiadLevel:
                                    if position_comp in position or "Любые" in position:
                                        if subject_comp == subject or "Любые" in subject or (subject_comp == "Другое" and subject == "Другой"):

                                            if _isEmpty:
                                                doc = docx.Document()
                                                paragraph = doc.add_paragraph()
                                                _isEmpty = False
                                            _Achievements_count += 1

                                            paragraph.add_run(f'Название конкурса: {name_comp}\n')
                                            paragraph.add_run(f'Вид конкурса: {type_comp}\n')
                                            paragraph.add_run(f'Дата проведения конкурса: {date}\n')
                                            paragraph.add_run(f'Занятое место: {position_comp}\n')
                                            paragraph.add_run(f'Уровень конкурса: {level_comp}\n')
                                            paragraph.add_run(f'Предмет конкурса: {subject_comp}\n')
                                            paragraph.add_run(f'Тип работы: {workType_comp}\n')
                                            paragraph.add_run(f'Тип документа: {docType_comp}\n')
                                            paragraph.add_run('\n')
                                            paragraph.add_run('\n')
                                            if downloadScans != None:
                                                file_format = achievements[key]["file_format"]
                                                encoded_file_path = f'{localId}/{key}.{file_format}'.replace('/', '%2F')
                                                url = f'https://firebasestorage.googleapis.com/v0/b/{firebaseConfig["storageBucket"]}/o/{encoded_file_path}?alt=media'
                                                response = requests.get(url)
                                                if response.status_code == 200:
                                                    file_path = os.path.join(f'{key}.{file_format}')
                                                    with open(file_path, 'wb') as file:
                                                        file.write(response.content)
                                                    with zipfile.ZipFile(f'{name}.zip', 'a', zipfile.ZIP_DEFLATED) as zipf:
                                                        zipf.write(file_path, arcname=f'{name_comp}/{name_comp}.{file_format}')

                                                    os.remove(file_path)

                                                else:
                                                        pass #todo: break point. warn message, о косяке/попробовать пропустить эту


            if _isEmpty:
                #todo: (сделано?) не сохранять пользователю, а прямо на сайте сказать, что по заданным параметрам нет достижений. !не нравится внешний вид. на телефонах надо по центру экрана делать соо

                name = "Нет результатов"
                return name, f'По заданным фильтрам не были найдены достижения'

            # todo: расскоментировать после того, как сделаешь мультивыбор для всего
            pretty_compTypes = ', '.join(competitionType)
            pretty_docTypes = ', '.join(documentType)
            pretty_posTypes = ', '.join(position)
            pretty_lvlTypes = ', '.join(olympiadLevel)
            pretty_workTypes = ', '.join(workType)
            pretty_subjectTypes = ', '.join(subject)

            # pretty_docTypes, pretty_posTypes, pretty_lvlTypes, pretty_workTypes, pretty_subjectTypes = documentType, position, olympiadLevel, workType, subject
            _wordForm, _foundForm = '', 'найдено'
            if _Achievements_count % 10 == 1 and _Achievements_count % 100 != 11:
                _wordForm, _foundForm = 'конкурс', 'найден'
            elif 2 <= _Achievements_count % 10 <= 4 and (_Achievements_count % 100 < 10 or _Achievements_count % 100 >= 20):
                _wordForm = 'конкурса'
            else:
                _wordForm = 'конкурсов'
            paragraph.add_run(f'Всего {_foundForm} {_Achievements_count} {_wordForm} по заданным параметрам:\n')
            paragraph.add_run(f'   Виды конкурсов: {pretty_compTypes}\n')
            paragraph.add_run(f'   Даты проведения конкурсов: {_StartDay}.{_StartMonth}.{_StartYear} — {_EndDay}.{_EndMonth}.{_EndYear}\n') #todo: fix вывод такой даты 1.1.1200 — 1.1.2050. почему нет 0 перед д.м -- хз, но это с StartDate связано
            paragraph.add_run(f'   Занятые места: {pretty_posTypes}\n')
            paragraph.add_run(f'   Уровени конкурсов: {pretty_lvlTypes}\n')
            paragraph.add_run(f'   Предметы конкурсов: {pretty_subjectTypes}\n')
            paragraph.add_run(f'   Тип работ: {pretty_workTypes}\n')
            paragraph.add_run(f'   Тип документов: {pretty_docTypes}\n')

            doc.save(f'{name}.docx')
            if downloadScans != None:
                with zipfile.ZipFile(f'{name}.zip', 'a', zipfile.ZIP_DEFLATED) as zipf:
                    zipf.write(f'{name}.docx', f'{name}.docx')

            return name, f'{key}'
        else:
            # todo: (в процессе) также, если у пользователя нет достижений, то в лоб ему тыкнуть, что у него их нет через алёрт, а эту штуку убрать
            name = "Нет результатов"
            return name, "У Вас нет добавленных достижений!"


    except Exception as e:
        print(f'forms.py| def generate_report | line 312|  !!!отчёт не сформирован\n{e}')
        return f'Отчёт не сформирован.\n{e}'


