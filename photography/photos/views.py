from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse, FileResponse
from django.db.models import Count
from django.urls import reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import login
import os
import mimetypes

from .models import Photo, Comment, Like
from .forms import UserRegisterForm, PhotoUploadForm, CommentForm


def home(request):
    """Homepage view showing recent photos"""
    photos = Photo.objects.all().order_by('-created_at')[:9]
    return render(request, 'photos/home.html', {'photos': photos})


class PhotoListView(ListView):
    """View for listing all photos with pagination"""
    model = Photo
    template_name = 'photos/photo_list.html'
    context_object_name = 'photos'
    ordering = ['-created_at']
    paginate_by = 12


class UserPhotoListView(ListView):
    """View for listing photos by a specific user"""
    model = Photo
    template_name = 'photos/user_photos.html'
    context_object_name = 'photos'
    paginate_by = 12

    def get_queryset(self):
        username = self.kwargs.get('username')
        return Photo.objects.filter(user__username=username).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['username'] = self.kwargs.get('username')
        return context


class PhotoDetailView(DetailView):
    """View for showing details of a photo"""
    model = Photo
    template_name = 'photos/photo_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm()
        
        # Check if user has liked this photo
        if self.request.user.is_authenticated:
            context['user_has_liked'] = Like.objects.filter(
                photo=self.object, user=self.request.user
            ).exists()
        
        return context


class PhotoCreateView(LoginRequiredMixin, CreateView):
    """View for uploading a new photo"""
    model = Photo
    form_class = PhotoUploadForm
    template_name = 'photos/photo_form.html'
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Your photo has been uploaded!')
        return super().form_valid(form)


class PhotoUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """View for updating an existing photo"""
    model = Photo
    form_class = PhotoUploadForm
    template_name = 'photos/photo_form.html'
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Your photo has been updated!')
        return super().form_valid(form)
    
    def test_func(self):
        photo = self.get_object()
        return self.request.user == photo.user


class PhotoDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """View for deleting a photo"""
    model = Photo
    template_name = 'photos/photo_confirm_delete.html'
    success_url = '/'
    
    def test_func(self):
        photo = self.get_object()
        return self.request.user == photo.user
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Your photo has been deleted!')
        return super().delete(request, *args, **kwargs)


def register(request):
    """User registration view"""
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Account created for {user.username}!')
            return redirect('home')
    else:
        form = UserRegisterForm()
    return render(request, 'photos/register.html', {'form': form})


@login_required
def add_comment(request, pk):
    """Add comment to a photo"""
    photo = get_object_or_404(Photo, pk=pk)
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.photo = photo
            comment.save()
            messages.success(request, 'Your comment has been added!')
            return redirect('photo_detail', pk=photo.pk)
    
    return redirect('photo_detail', pk=photo.pk)


@login_required
def like_photo(request, pk):
    """Toggle like/unlike a photo"""
    photo = get_object_or_404(Photo, pk=pk)
    like, created = Like.objects.get_or_create(user=request.user, photo=photo)
    
    if not created:
        # User already liked this photo, so unlike it
        like.delete()
        liked = False
    else:
        # New like created
        liked = True
    
    # For AJAX requests
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'liked': liked,
            'like_count': photo.like_count
        })
    
    # For regular form submission
    return HttpResponseRedirect(reverse('photo_detail', args=[photo.id]))


@login_required
def download_photo(request, pk):
    """Download the photo file"""
    photo = get_object_or_404(Photo, pk=pk)
    
    # Get the file path and name
    file_path = photo.image.path
    filename = os.path.basename(file_path)
    
    # Determine content type
    content_type, _ = mimetypes.guess_type(file_path)
    if not content_type:
        content_type = 'application/octet-stream'  # Default content type
        
    # Create file response with proper content disposition for download
    response = FileResponse(open(file_path, 'rb'), content_type=content_type)
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response
