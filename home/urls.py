from django.urls import path, include
from . import views

app_name="home"
urlpatterns = [


    path('', views.HomeView.as_view(), name="homepage"),
    path('register/',views.register_user, name="register"),

    path('password-reset/',views.password_reset, name="password-reset"),
    path('set-password/',views.set_password, name="set-password"),
    path('login/', views.my_login_view, name='custom_login'),

    ]
