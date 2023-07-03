from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', homepage),
    path('authorization', authorization, name='auth'),
    path('profile', profile, name='profile'),
    path('add_achievement', add_achievement, name='add_achievement'),
    path('list_achievements', list_achievements, name='list_achievements'),
    path('make_report', make_report, name='make_report'),
    path('logout', logout, name='logout'),
    # path('postsignin', postsignin)
    # path('account')
]