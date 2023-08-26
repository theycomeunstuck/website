from django import forms
import pyrebase, urllib3, json, datetime, requests, docx, zipfile, os
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
    # try:
    localId = request.COOKIES['user_localId']
    idToken = request.COOKIES['user_idToken']

    competitionType = request.POST.getlist("competitionType") # ['Любые', 'Олимпиада'] (как массив)
    documentType = request.POST.get("documentType") #сертификат грамота диплом благодарность
    startDate = str(request.POST.get("startDate")).replace("-", ".")
    endDate = str(request.POST.get("endDate")).replace("-", ".")
    position = request.POST.get("position")
    olympiadLevel = request.POST.get("olympiadLevel")
    workType = request.POST.get("workType")
    subject = request.POST.get("subject")
    downloadScans = request.POST.get("downloadScans") #False == None | True = "on"
    _isEmpty, name, doc, paragraph = True, f'Отчёт {startDate} — {endDate}', "", ""
    achievements = db.child("users").child(localId).child("achievements").get().val()
    startDate = datetime.datetime.strptime(startDate, "%Y.%m.%d").date()
    endDate = datetime.datetime.strptime(endDate, "%Y.%m.%d").date()


    # print(achievements, "\n\n\n")
    if achievements:
        for key in achievements: #todo: НАПИСАТЬ ХУЙНЮ КОТОРАЯ ОЧИСТИТ ОТ АЧИВОК С КРИВОЙ ДАТОЙ (YMD) И СЛИШКМО МАЛЕНЬКИМИ/БОЛЬШИМИ НУ ТИПО КАК НЕГРОВ СДЕЛАТЬ
            print("hi")
            name_comp = achievements[key]['competition_name'] #Названике работы
            type_comp = achievements[key]['competition_type'] #Вид конкурса
            level_comp = achievements[key]["level_competition"] #Уровень конкурса
            position_comp = achievements[key]["place"] #Занятое место
            subject_comp = achievements[key]["subject"] #Предметы
            workType_comp = achievements[key]["work_type"] #Вид работы (Решение задач, выступление)
            docType_comp = achievements[key]["type_document"] #Вид документа
            print(key, name_comp)
            compDate = datetime.datetime.strptime(achievements[key]['date'], "%d.%m.%Y").date()
            print(f'{achievements[key]}\n')
            if startDate <= compDate <= endDate: #todo: сделать мультивыбор в фильтре, а затем убрать |(     or XXX_comp == XXX)
            #     if type_comp in competitionType or "Любые" in competitionType or (type_comp == competitionType):
            #         if workType_comp == workType or "Любые" in workType or (workType_comp == workType):
            #             if docType_comp in documentType or "Любые" in documentType or (docType_comp == documentType):
            #                 if level_comp in olympiadLevel or "Любые" in olympiadLevel or (level_comp == olympiadLevel):
            #                     if position_comp in position or "Любые" in position or (position_comp == position):
            #                         if subject_comp == subject or "Любые" in subject or (subject_comp == subject) or (subject_comp == "Другое" and subject == "Другой"): #todo: костыльебауный

                if _isEmpty:
                    doc = docx.Document()
                    paragraph = doc.add_paragraph()
                    _isEmpty = False

                paragraph.add_run(f'Название конкурса: {name_comp}\n')
                paragraph.add_run(f'Вид конкурса: {type_comp}\n')
                paragraph.add_run(f'Дата проведения конкурса: {compDate}\n')
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
                            pass #todo: break point. warn message, о косяке/попробовать пропустить хуйню эту


        if _isEmpty:
            #todo: (сделано?) не сохранять пользователю, а прямо на сайте сказать, что по заданным параметрам нет достижений.
            name = "Нет результатов"
            return name, f'По заданным фильтрам не были найдены достижения'

        #todo: запись сколько всего достижений с такими параметрами и какие фильтры были выбраны
        pretty_compTypes, pretty_docTypes, pretty_posTypes, pretty_lvlTypes, pretty_workTypes, pretty_subjectTypes= '', '','','','',''
        for type in competitionType:
            pretty_compTypes = f'{pretty_compTypes}, {type}'

        # todo: расскоментировать после того, как сделаешь мультивыбор для всей хуйни
        pretty_docTypes, pretty_posTypes, pretty_lvlTypes, pretty_workTypes, pretty_subjectTypes = documentType, position, olympiadLevel, workType, subject
        # for type in documentType:
        #     pretty_docTypes = f'{pretty_docTypes}, {type}'
        # for type in position:
        #     pretty_posTypes = f'{pretty_posTypes}, {type}'
        # for type in olympiadLevel:
        #     pretty_lvlTypes = f'{pretty_lvlTypes}, {type}'
        # for type in workType:
        #     pretty_workTypes = f'{pretty_workTypes}, {type}'
        # for type in subject:
        #     pretty_subjectTypes = f'{pretty_subjectTypes}, {type}'
        _wordForm, _foundForm = '', ''
        word_forms_count = ['найден', 'найдено', 'найдено']        if _Achievements_count % 10 == 1 and _Achievements_count % 100 != 11:
            _wordForm = 'конкурс'
        elif 2 <= _Achievements_count % 10 <= 4 and (_Achievements_count % 100 < 10 or _Achievements_count % 100 >= 20):
            _wordForm = 'конкурса'
        else:
            _wordForm = 'конкурсов'
        paragraph.add_run(f'Всего {_foundForm} {_Achievements_count} {_wordForm} по заданным параметрам:\n')
        paragraph.add_run(f'   Виды конкурсов: {pretty_compTypes}\n')
        paragraph.add_run(f'   Даты проведения конкурсов: {startDate} — {endDate}\n')
        paragraph.add_run(f'   Занятые места: {pretty_posTypes}\n')
        paragraph.add_run(f'   Уровени конкурсов: {pretty_lvlTypes}\n')
        paragraph.add_run(f'   Предметы конкурсов: {pretty_subjectTypes}\n')
        paragraph.add_run(f'   Тип работ: {pretty_workTypes}\n')
        paragraph.add_run(f'   Тип документов: {pretty_docTypes}\n')
        doc.save(f'  \n')
        doc.save(f'{name}.docx')
        if downloadScans != None:
            with zipfile.ZipFile(f'{name}.zip', 'a', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(f'{name}.docx', f'{name}.docx')

        return name, f'{key}'
    else:
        # todo: (в процессе) также, если у пользователя нет достижений, то в лоб ему тыкнуть, что у него их нет через алёрт. а эту штуку убрать
        name = "Нет результатов"
        return name, "У Вас нет добавленных достижений!"

    #
    # except Exception as e:
    #     print(f'forms.py| def generate_report | line 312|  !!!отчёт не сформирован\n{e}')
    #     return f'Отчёт не сформирован.\n{e}'


