from django.shortcuts import render, HttpResponse

# Create your views here.
def index(request):
    return render(request, 'main/index.html')

def hello(request):
    return HttpResponse("Hello Django")

def func(request):
    return HttpResponse('You are on the None page!')