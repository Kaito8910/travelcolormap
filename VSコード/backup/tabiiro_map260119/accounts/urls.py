from django.urls import path
from . import views

app_name = 'accounts'
urlpatterns = [
    path('', views.base.as_view(), name='base'),
    path('change_pwd/', views.ChangePwd.as_view(), name='change_pwd'),
    path('change_pwd_finish/', views.ChangePwdFinish.as_view(), name='change_pwd_finish'),
]

from django.urls import path
from . import views

urlpatterns = [
    # ...既存のURL...
    path('user/data/', views.user_data, name='user_data'),
]