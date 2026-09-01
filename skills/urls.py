from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='index'),
    path('skills/', views.skill_list, name='skill_list'),
    path('<int:pk>/', views.skill_detail, name='skill_detail'),
]