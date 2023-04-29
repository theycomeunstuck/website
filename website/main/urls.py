from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', homepage),
    path('authorization', authorization, name='auth'),
    path('profile', profile, name='profile'),
    path('add_achievement', add_achievements, name='add'),
    path('list_achievements', list_achievements, name='list'),
    path('make_achievement', make_report, name='make'),
    # path('postsignin', postsignin)
    # path('account')
]