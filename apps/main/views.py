from django.shortcuts import render, HttpResponse
#from .models import
# Create your views here.
def index(request):
    return render(request, 'main/index.html')
    posts = Post.objects.a

def func(request):
    return HttpResponse('You are on the None page!')

def sample(request):
    return render(request, 'blog/base.html')