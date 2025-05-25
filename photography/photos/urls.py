from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('photos/', views.PhotoListView.as_view(), name='photo_list'),
    path('photos/user/<str:username>/', views.UserPhotoListView.as_view(), name='user_photos'),
    path('photos/<int:pk>/', views.PhotoDetailView.as_view(), name='photo_detail'),
    path('photos/new/', views.PhotoCreateView.as_view(), name='photo_create'),
    path('photos/<int:pk>/update/', views.PhotoUpdateView.as_view(), name='photo_update'),
    path('photos/<int:pk>/delete/', views.PhotoDeleteView.as_view(), name='photo_delete'),
    path('photos/<int:pk>/comment/', views.add_comment, name='add_comment'),
    path('photos/<int:pk>/like/', views.like_photo, name='like_photo'),
    path('photos/<int:pk>/download/', views.download_photo, name='download_photo'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='photos/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='photos/logout.html'), name='logout'),
] 