from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, auth
from django.contrib.auth import authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Profile

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            auth.login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'Invalid credentials!')
            return redirect('login')
            
    return render(request, 'auth/login.html')

def register(request):
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password1')

        if not username or not email or not password:
            messages.error(request, 'All fields are required.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            # Profile is auto-created via signal
            
            messages.success(request, 'Registration successful. Sign in now!')
            return redirect('login')
    
    return render(request, 'auth/register.html')

@login_required
def user_profile(request, username=None):
    """
    Display user profile page
    If username is provided, show that user's profile
    Otherwise show the logged-in user's profile
    """
    # Get the user to display
    if username:
        profile_user = get_object_or_404(User, username=username)
    else:
        profile_user = request.user
    
    # Get or create profile (just in case)
    profile, created = Profile.objects.get_or_create(user=profile_user)
    
    # These will be populated later when you add Skill, Swap, Review models
    # For now, passing empty lists or 0 values
    skills_offered_list = []  # Will be populated later
    skills_wanted_list = []   # Will be populated later
    reviews_list = []         # Will be populated later
    activity_list = []        # Will be populated later
    
    context = {
        'profile_user': profile_user,
        'skills_offered': 0,
        'skills_wanted': 0,
        'completed_swaps': 0,
        'connections': 0,
        'skills_offered_list': skills_offered_list,
        'skills_wanted_list': skills_wanted_list,
        'reviews_list': reviews_list,
        'activity_list': activity_list,
    }
    
    return render(request, 'auth/profile.html', context)

def logout_view(request):
    logout(request)
    return redirect('index')