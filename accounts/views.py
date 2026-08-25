from django.shortcuts import render, redirect

def login(request):
    return render(request, 'auth/login.html')

def register(request):
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # username, email and password validation logic
        # new user creation logic
    
    return render(request, 'auth/register.html')