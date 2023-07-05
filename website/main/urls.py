from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    #path('route', функция, 'переменная этой url')
    path('admin/', admin.site.urls),
    path('', homepage),
    path('authorization', authorization, name='auth'),
    path('profile', profile, name='profile'),
    path('add-achievement', add_achievement, name='add_achievement'),
    path('list-achievements', list_achievements, name='list_achievements'),
    path('make-report', make_report, name='make_report'),
    path('logout', logout, name='logout'),

]