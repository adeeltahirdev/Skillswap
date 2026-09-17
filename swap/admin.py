from django.contrib import admin
from .models import SwapRequest, Review, Activity, Notification, Message

@admin.register(SwapRequest)
class SwapRequestAdmin(admin.ModelAdmin):
    list_display = ('requester', 'recipient', 'offered_skill', 'requested_skill', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('requester__username', 'recipient__username', 'offered_skill__name', 'requested_skill__name')
    actions = ['mark_completed']

    @admin.action(description='Mark selected swaps as completed')
    def mark_completed(self, request, queryset):
        queryset.filter(status='accepted').update(status='completed')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('reviewer', 'user', 'rating', 'swap', 'created_at')
    list_filter = ('rating', 'created_at')

admin.site.register(Activity)
admin.site.register(Notification)
admin.site.register(Message)
