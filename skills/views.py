from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Skill


def home(request):
    return render(request, 'index.html')

def skill_list(request):
    """
    Display list of all skills with filtering and search
    """
    # Get all skills
    skills = Skill.objects.all().select_related('user', 'user__profile')
    
    # Search filter
    search_query = request.GET.get('q')
    if search_query:
        skills = skills.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(user__username__icontains=search_query)
        )
    
    # Category filter
    category = request.GET.get('category')
    if category:
        skills = skills.filter(category=category)
    
    # Skill type filter
    skill_type = request.GET.get('type')
    if skill_type:
        skills = skills.filter(skill_type=skill_type)
    
    # Sorting
    sort_by = request.GET.get('sort', 'newest')
    if sort_by == 'newest':
        skills = skills.order_by('-created_at')
    elif sort_by == 'rating':
        skills = skills.order_by('-user__profile__rating')
    elif sort_by == 'popular':
        skills = skills.order_by('-user__profile__reviews_count')
    elif sort_by == 'az':
        skills = skills.order_by('name')
    
    # Pagination
    paginator = Paginator(skills, 12)  # 12 skills per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'skills': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
    }
    
    return render(request, 'skills/skill_list.html', context)