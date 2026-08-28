from django.db import models
from django.contrib.auth.models import User

class Skill(models.Model):
    SKILL_TYPES = [
        ('offer', 'I can teach this'),
        ('want', 'I want to learn this'),
    ]
    
    CATEGORY_CHOICES = [
        ('programming', 'Programming'),
        ('design', 'Design'),
        ('music', 'Music'),
        ('arts', 'Arts'),
        ('language', 'Language'),
        ('business', 'Business'),
        ('fitness', 'Fitness'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='skills')
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    skill_type = models.CharField(max_length=10, choices=SKILL_TYPES)
    description = models.TextField(max_length=500, blank=True)
    icon = models.CharField(max_length=50, default='bi bi-tools')
    color = models.CharField(max_length=100, default='linear-gradient(135deg, #7c3aed, #8b5cf6)')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.name} ({self.get_skill_type_display()})"