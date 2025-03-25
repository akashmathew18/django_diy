from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy
from django.contrib.auth import views as auth_views
from .views import signup

app_name = 'blog'

urlpatterns = [
    # Authentication views
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    
   
    
    # Home and post views
    path('', views.home, name='home'),
    path('post/create/', views.post_create, name='post_create'),
    path('post/<slug:slug>/', views.post_detail, name='post_detail'),
    path('post/<slug:slug>/edit/', views.post_edit, name='post_edit'),
    path('post/<slug:slug>/delete/', views.post_delete, name='post_delete'),
    
    # Tag views
    path('tag/<slug:slug>/', views.tag_posts, name='tag_posts'),
    
    # Comment views
    path('post/<slug:slug>/comment/', views.add_comment, name='add_comment'),
    path('comment/<int:pk>/reply/', views.reply_comment, name='reply_comment'),
    path('comment/<int:pk>/delete/', views.delete_comment, name='delete_comment'),
    
    # Like/Dislike views
    path('post/<slug:slug>/like/', views.like_post, name='like_post'),
    path('post/<slug:slug>/dislike/', views.dislike_post, name='dislike_post'),
    
    # User profile views
    path('profile/<str:username>/', views.user_profile, name='user_profile'),
    path('profile/<str:username>/edit/', views.profile_edit, name='profile_edit'),
    path('profile/delete/', views.delete_account, name='delete_account'),
    
    # Search and filter views
    path('search/', views.search_posts, name='search_posts'),
    path('filter/', views.filter_posts, name='filter_posts'),
    
    # Dashboard views
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/posts/', views.user_posts, name='user_posts'),
    path('dashboard/comments/', views.user_comments, name='user_comments'),
] 