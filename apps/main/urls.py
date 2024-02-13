from django.urls import path
from . import views
from django.views.generic import TemplateView

urlpatterns = [
    path('', views.index, name= 'index'),
    # path('lol', views.index, name='about'),
    path('about', TemplateView.as_view(template_name="main/about.html")),
    path('home', TemplateView.as_view(template_name="main/index.html")),
    path('for_us', TemplateView.as_view(template_name="main/for_us.html")),
    path('contacts', TemplateView.as_view(template_name="main/contacts.html")),
    path('veterinarsadvice', TemplateView.as_view(template_name="main/veterinarsadvice.html"))
]
