from django.urls import path
from . import views
from django.views.generic import TemplateView
app_name = 'main'
urlpatterns = [
    path('', views.index, name= 'index'),
    # path('lol', views.index, name='about'),
    path('about', views.index, name='about'),
    path('for_us', views.index, name='for_us'),
    path('contacts', views.index, name='contacts'),
    path('veterinarsadvive', views.index, name='veterinarsadvice'),
    path('article', views.index, name='blog/index')
]
