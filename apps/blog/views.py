from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import Post, Comment
from .forms import PostForm, CommentForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages


# Create your views here.
# @login_required
def index(request):
    posts = Post.objects.filter(is_published=True)
    create_form = PostForm()

    context = {
        'posts': posts,
        'form': create_form
    }

    return render(request, 'blog/index.html', context)


@login_required
def post(request, post_id):
    # post = Post.objects.get(id=post_id)
    form_comment = CommentForm()
    post = get_object_or_404(Post, id=post_id)
    post.views += 1
    post.save()
    context = {
        'post': post,
        'comment_form': form_comment,
    }

    return render(request, 'blog/post.html', context)

@login_required
def posts(request):
    posts = Post.objects.all()
    form_create_post = PostForm()
    context = {
        'posts': posts,
        'form_create_post': form_create_post
    }

    return render(request, 'blog/index.html', context)


@login_required
def create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, 'Пост створено')
    return redirect('blog:index')


@login_required
def comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            print(comment)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, 'Коментар додано')
    return redirect('blog:post', post_id=post_id)


@login_required
def like(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)

    if request.user in post.dislikes.all():
        post.dislikes.remove(request.user)

    post.save()
    return JsonResponse({
        'dislikes': post.dislikes.count(),
        'likes': post.likes.count()})

@login_required
def dislike(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user in post.dislikes.all():
        post.dislikes.remove(request.user)
    else:
        post.dislikes.add(request.user)

    if request.user in post.likes.all():
        post.likes.remove(request.user)

    post.save()
    return JsonResponse({
        'dislikes': post.dislikes.count(),
        'likes': post.likes.count()})


@login_required
def like_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, post__id=post_id)
    if request.user in comment.likes.all():
        comment.likes.remove(request.user)
    else:
        comment.likes.add(request.user)
    comment.save()
    return JsonResponse({'likes': comment.likes.count()})

@login_required
def dislike_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, post__id=post_id)
    if request.user in comment.dislikes.all():
        comment.dislikes.remove(request.user)
    else:
        comment.dislikes.add(request.user)
    comment.save()
    return JsonResponse({'dislikes': comment.dislikes.count()})


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)
    post.delete()
    messages.success(request, 'Пост видалено')
    return redirect('members:profile')

@login_required
def redact_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)

    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Пост змінено')
            return redirect('members:profile')
        else:
            messages.error(request, 'Форма має помилки. Будь ласка, виправте їх.')
    else:
        form = PostForm(instance=post)

    return redirect('members:profile')