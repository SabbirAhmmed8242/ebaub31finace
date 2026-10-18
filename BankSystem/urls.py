from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin_page/', views.Admin, name='adminpage'),
    path('', views.Home, name="Home"),
    path('login/', views.Login, name='Login'),
    path('registration/', views.Registration, name='registration'),
    path('profile/', views.profile, name='profile'),
    path('Log-out/', views.LogOut, name='Logout'),
    path('errpage/', views.errpage, name='errpage'),
]
