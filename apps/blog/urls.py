from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.posts, name='index'),
    path('<int:post_id>/', views.post, name='post'),
    path('create/', views.create, name='create'),
    path('<int:post_id>/comment/', views.comment, name='comment'),
    path('<int:post_id>/like/', views.like, name='like'),
    path('<int:post_id>/dislike/', views.dislike, name='dislike'),
    path('<int:post_id>/comment/<int:comment_id>/like/', views.like_comment, name='like_comment'),
    path('<int:post_id>/comment/<int:comment_id>/dislike/', views.like_comment, name='dislike_comment'),
    path('<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('<int:post_id>/redact/', views.redact_post, name='redact_post')
]