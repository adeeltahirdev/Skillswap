from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.models import User
from .models import Skill

def home(request):
    """
    Home page - shows featured skills
    """
    # Get featured skills (latest 6 skills)
    featured_skills = Skill.objects.all().select_related('user', 'user__profile').order_by('-created_at')[:6]
    
    # Get counts
    total_skills = Skill.objects.count()
    total_users = User.objects.count()
    
    context = {
        'featured_skills': featured_skills,
        'total_skills': total_skills,
        'total_users': total_users,
    }
    
    return render(request, 'index.html', context)

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
    paginator = Paginator(skills, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'skills': page_obj,
    }
    
    return render(request, 'skills/skill_list.html', context)

def skill_detail(request, pk):
    """
    Display detailed view of a single skill
    """
    skill = get_object_or_404(Skill.objects.select_related('user', 'user__profile'), pk=pk)
    
    # Get similar skills (same category, exclude current)
    similar_skills = Skill.objects.filter(
        category=skill.category
    ).exclude(
        id=skill.id
    ).select_related('user')[:4]
    
    context = {
        'skill': skill,
        'similar_skills': similar_skills,
    }
    
    return render(request, 'skills/skill_detail.html', context)