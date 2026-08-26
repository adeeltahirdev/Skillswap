from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib.auth import authenticate, logout
from django.contrib import messages

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
            
    return render(request, 'auth/login.html')

def register(request):
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password1')
        confirm_password = request.POST.get('password2')

        if not username or not email or not password:
            messages.error(request, 'All fields are required.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
        elif password != confirm_password:
            messages.error(request, 'Passwords do not match.')
        else:
            User.objects.create_user(username=username, email=email, password=password)
            messages.success(request, 'Registration successful. Sign in now!')
            return redirect('login')
    
    return render(request, 'auth/register.html')

def logout(request):
    logout(request)
    return redirect('index')