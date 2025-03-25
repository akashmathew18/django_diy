from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Post, Comment, UserProfile, Like, Dislike, Category
from .forms import PostForm, CommentForm, UserProfileForm, SignupForm, LoginForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout
from taggit.models import Tag

def home(request):
    posts = Post.objects.filter(status='published')
    paginator = Paginator(posts, 5)
    page = request.GET.get('page')
    posts = paginator.get_page(page)
    categories = Category.objects.all()
    recent_posts = Post.objects.filter(status='published').order_by('-created_at')[:5]
    return render(request, 'blog/home.html', {
        'posts': posts,
        'categories': categories,
        'recent_posts': recent_posts,
    })

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            remember_me = form.cleaned_data.get('remember_me', False)
            
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)
                if not remember_me:
                    # Session expires when browser closes
                    request.session.set_expiry(0)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('blog:home')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    return render(request, 'blog/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('blog:home')

def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, status='published')
    post.views += 1
    post.save()
    comments = post.comments.filter(parent=None)
    return render(request, 'blog/post_detail.html', {
        'post': post,
        'comments': comments,
        'comment_form': CommentForm()
    })

@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.status = 'published'
            post.save()
            form.save_m2m()
            messages.success(request, 'Post created successfully!')
            return redirect('blog:post_detail', slug=post.slug)
    else:
        form = PostForm()
    return render(request, 'blog/post_form.html', {'form': form})

@login_required
def post_edit(request, slug):
    post = get_object_or_404(Post, slug=slug, author=request.user)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Post updated successfully!')
            return redirect('blog:post_detail', slug=post.slug)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_form.html', {'form': form, 'title': 'Edit Post'})

@login_required
def post_delete(request, slug):
    post = get_object_or_404(Post, slug=slug, author=request.user)
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post deleted successfully!')
        return redirect('blog:home')
    return render(request, 'blog/post_confirm_delete.html', {'post': post})

@login_required
@require_POST
def like_post(request, slug):
    post = get_object_or_404(Post, slug=slug)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    if not created:
        like.delete()
        liked = False
    else:
        Dislike.objects.filter(user=request.user, post=post).delete()
        liked = True
    return JsonResponse({'liked': liked, 'likes_count': post.likes.count(), 'dislikes_count': post.dislikes.count()})

@login_required
@require_POST
def dislike_post(request, slug):
    post = get_object_or_404(Post, slug=slug)
    dislike, created = Dislike.objects.get_or_create(user=request.user, post=post)
    if not created:
        dislike.delete()
        disliked = False
    else:
        Like.objects.filter(user=request.user, post=post).delete()
        disliked = True
    return JsonResponse({'disliked': disliked, 'likes_count': post.likes.count(), 'dislikes_count': post.dislikes.count()})

def user_profile(request, username):
    user = get_object_or_404(User, username=username)
    profile, created = UserProfile.objects.get_or_create(user=user)
    posts = Post.objects.filter(author=user, status='published')
    return render(request, 'blog/user_profile.html', {'profile': profile, 'posts': posts})

@login_required
def profile_edit(request, username):
    if request.user.username != username:
        return redirect('blog:user_profile', username=username)
    profile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('blog:user_profile', username=username)
    else:
        form = UserProfileForm(instance=profile)
    return render(request, 'blog/profile_form.html', {'form': form})

def search_posts(request):
    query = request.GET.get('q', '')
    posts = Post.objects.filter(Q(title__icontains=query) | Q(content__icontains=query) | Q(author__username__icontains=query), status='published')
    paginator = Paginator(posts, 5)
    page = request.GET.get('page')
    posts = paginator.get_page(page)
    return render(request, 'blog/search_results.html', {'posts': posts, 'query': query})

def filter_posts(request):
    category = request.GET.get('category')
    author = request.GET.get('author')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    posts = Post.objects.filter(status='published')

    if category:
        posts = posts.filter(category__slug=category)
    if author:
        posts = posts.filter(author__username=author)
    if date_from:
        posts = posts.filter(created_at__gte=date_from)
    if date_to:
        posts = posts.filter(created_at__lte=date_to)

    paginator = Paginator(posts, 5)
    page = request.GET.get('page')
    posts = paginator.get_page(page)

    return render(request, 'blog/filtered_posts.html', {'posts': posts})

@login_required
def dashboard(request):
    return render(request, 'blog/dashboard.html')

@login_required
def user_posts(request):
    posts = Post.objects.filter(author=request.user)
    paginator = Paginator(posts, 5)
    page = request.GET.get('page')
    posts = paginator.get_page(page)
    return render(request, 'blog/user_posts.html', {'posts': posts})

@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, 'Your account has been deleted successfully.')
        return redirect('blog:home')
    return render(request, 'blog/delete_account.html')

def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST, request.FILES)
        if form.is_valid():
            # Create the user object but don't save it yet
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password1'],
                first_name=form.cleaned_data.get('first_name', ''),
                last_name=form.cleaned_data.get('last_name', '')
            )
            
            # Create user profile
            profile = UserProfile.objects.create(
                user=user,
                bio=form.cleaned_data.get('bio', ''),
                profile_picture=form.cleaned_data.get('profile_picture', None)
            )
            
            messages.success(request, 'Account created successfully! Please login to continue.')
            return redirect('blog:login')
        else:
            # If form is not valid, add error message
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SignupForm()
    return render(request, 'blog/signup.html', {'form': form})

def tag_posts(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    posts = Post.objects.filter(tags__name__in=[tag.name], status='published')
    paginator = Paginator(posts, 5)
    page = request.GET.get('page')
    posts = paginator.get_page(page)
    return render(request, 'blog/tag_posts.html', {
        'tag': tag,
        'posts': posts,
    })

@login_required
def add_comment(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            
            # Handle reply to another comment
            parent_id = request.POST.get('parent_id')
            if parent_id:
                parent_comment = get_object_or_404(Comment, id=parent_id)
                comment.parent = parent_comment
            
            comment.save()
            messages.success(request, 'Your comment has been added successfully!')
            return redirect('blog:post_detail', slug=post.slug)
    return redirect('blog:post_detail', slug=post.slug)

@login_required
def reply_comment(request, pk):
    parent_comment = get_object_or_404(Comment, pk=pk)
    post = parent_comment.post
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.post = post
            reply.author = request.user
            reply.parent = parent_comment
            reply.save()
            messages.success(request, 'Your reply has been added successfully!')
    
    return redirect('blog:post_detail', slug=post.slug)

@login_required
def user_comments(request):
    comments = Comment.objects.filter(author=request.user).order_by('-created_at')
    paginator = Paginator(comments, 10)
    page = request.GET.get('page')
    comments = paginator.get_page(page)
    return render(request, 'blog/user_comments.html', {'comments': comments})

@login_required
def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk, author=request.user)
    post = comment.post
    if request.method == 'POST':
        comment.delete()
        messages.success(request, 'Comment deleted successfully!')
    return redirect('blog:post_detail', slug=post.slug)
