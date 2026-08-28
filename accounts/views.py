from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import models
from .models import Profile  # Only import Profile from accounts
from skills.models import Skill  # Import Skill from skills app
from swap.models import SwapRequest, Review, Activity  # Import from swap app
import json

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            auth_login(request, user)
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
    
    # Get or create profile
    profile, created = Profile.objects.get_or_create(user=profile_user)
    
    # Get skills - Import Skill from skills app
    try:
        from skills.models import Skill
        skills_offered_list = Skill.objects.filter(user=profile_user, skill_type='offer')
        skills_wanted_list = Skill.objects.filter(user=profile_user, skill_type='want')
        skills_offered_count = skills_offered_list.count()
        skills_wanted_count = skills_wanted_list.count()
    except:
        skills_offered_list = []
        skills_wanted_list = []
        skills_offered_count = 0
        skills_wanted_count = 0
    
    # Get reviews and activity - Import from swap app
    try:
        from swap.models import SwapRequest, Review, Activity
        reviews_list = Review.objects.filter(user=profile_user).order_by('-created_at')[:10]
        activity_list = Activity.objects.filter(user=profile_user).order_by('-created_at')[:10]
        completed_swaps_count = SwapRequest.objects.filter(
            models.Q(requester=profile_user) | models.Q(recipient=profile_user),
            status='completed'
        ).count()
    except:
        reviews_list = []
        activity_list = []
        completed_swaps_count = 0
    
    connections_count = 0  # You can implement this later
    
    context = {
        'profile_user': profile_user,
        'skills_offered': skills_offered_count,
        'skills_wanted': skills_wanted_count,
        'completed_swaps': completed_swaps_count,
        'connections': connections_count,
        'skills_offered_list': skills_offered_list,
        'skills_wanted_list': skills_wanted_list,
        'reviews_list': reviews_list,
        'activity_list': activity_list,
    }
    
    return render(request, 'auth/profile.html', context)

@login_required
@require_POST
def update_profile(request):
    """
    AJAX endpoint to update user profile
    """
    try:
        data = json.loads(request.body)
        user = request.user
        profile = user.profile
        
        # Update fields
        if 'full_name' in data:
            user.first_name = data['full_name']
            user.save()
        
        if 'location' in data:
            profile.location = data['location']
        
        if 'bio' in data:
            profile.bio = data['bio']
        
        profile.save()
        
        # Create activity - Import from swap app
        try:
            from swap.models import Activity
            Activity.objects.create(
                user=user,
                title='Updated profile',
                description='Updated profile information',
                icon='bi bi-person-gear',
                color='linear-gradient(135deg, #7c3aed, #8b5cf6)'
            )
        except:
            pass
        
        return JsonResponse({
            'success': True,
            'message': 'Profile updated successfully!'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)

@login_required
@require_POST
def update_avatar(request):
    """
    AJAX endpoint to update user avatar
    """
    try:
        if request.FILES.get('avatar'):
            user = request.user
            profile = user.profile
            profile.avatar = request.FILES['avatar']
            profile.save()
            
            # Create activity
            try:
                from swap.models import Activity
                Activity.objects.create(
                    user=user,
                    title='Updated avatar',
                    description='Changed profile picture',
                    icon='bi bi-camera',
                    color='linear-gradient(135deg, #06b6d4, #10b981)'
                )
            except:
                pass
            
            return JsonResponse({
                'success': True,
                'message': 'Avatar updated successfully!',
                'avatar_url': profile.avatar.url
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'No image provided'
            }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)

@login_required
@require_POST
def add_skill(request):
    """
    AJAX endpoint to add a new skill
    """
    try:
        data = json.loads(request.body)
        user = request.user
        
        # Import Skill from skills app
        from skills.models import Skill
        
        # Get color based on skill category
        color_map = {
            'programming': 'linear-gradient(135deg, #7c3aed, #8b5cf6)',
            'design': 'linear-gradient(135deg, #06b6d4, #10b981)',
            'music': 'linear-gradient(135deg, #ec4899, #8b5cf6)',
            'arts': 'linear-gradient(135deg, #f59e0b, #ef4444)',
            'language': 'linear-gradient(135deg, #6366f1, #8b5cf6)',
            'business': 'linear-gradient(135deg, #10b981, #06b6d4)',
            'fitness': 'linear-gradient(135deg, #ef4444, #ec4899)',
            'other': 'linear-gradient(135deg, #6b7280, #9ca3af)',
        }
        
        # Icon mapping
        icon_map = {
            'programming': 'bi bi-code-square',
            'design': 'bi bi-palette',
            'music': 'bi bi-music-note-beamed',
            'arts': 'bi bi-camera',
            'language': 'bi bi-chat-dots',
            'business': 'bi bi-graph-up-arrow',
            'fitness': 'bi bi-heart-pulse',
            'other': 'bi bi-tools',
        }
        
        skill = Skill.objects.create(
            user=user,
            name=data['name'],
            category=data['category'],
            skill_type=data['skill_type'],
            description=data.get('description', ''),
            icon=icon_map.get(data['category'], 'bi bi-tools'),
            color=color_map.get(data['category'], 'linear-gradient(135deg, #7c3aed, #8b5cf6)')
        )
        
        # Create activity
        try:
            from swap.models import Activity
            skill_type_display = 'offered' if data['skill_type'] == 'offer' else 'wanted'
            Activity.objects.create(
                user=user,
                title='Added a new skill',
                description=f'Added "{data["name"]}" to skills {skill_type_display}',
                icon='bi bi-plus-circle',
                color='linear-gradient(135deg, #10b981, #06b6d4)'
            )
        except:
            pass
        
        return JsonResponse({
            'success': True,
            'message': 'Skill added successfully!',
            'skill': {
                'id': skill.id,
                'name': skill.name,
                'category': skill.get_category_display(),
                'skill_type': skill.skill_type,
                'icon': skill.icon,
                'color': skill.color
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)

@login_required
@require_POST
def delete_skill(request, skill_id):
    """
    AJAX endpoint to delete a skill
    """
    try:
        from skills.models import Skill
        skill = get_object_or_404(Skill, id=skill_id, user=request.user)
        skill_name = skill.name
        skill.delete()
        
        # Create activity
        try:
            from swap.models import Activity
            Activity.objects.create(
                user=request.user,
                title='Removed a skill',
                description=f'Removed "{skill_name}" from skills',
                icon='bi bi-trash',
                color='linear-gradient(135deg, #ef4444, #dc2626)'
            )
        except:
            pass
        
        return JsonResponse({
            'success': True,
            'message': 'Skill deleted successfully!'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)

def logout_view(request):
    logout(request)
    return redirect('index')