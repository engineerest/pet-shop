from django.urls import path
from . import views
from django.views.generic import TemplateView

urlpatterns = [
    path('', views.index, name= 'index'),
    # path('lol', views.index, name='about'),
    path('lol', TemplateView.as_view(template_name="main/about.html")),
    path('home', TemplateView.as_view(template_name="main/index.html"))
]
