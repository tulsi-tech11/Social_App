from xml.etree.ElementTree import Comment
from myapp.models import FollowUsers
from django.contrib import admin
from .models import * 
# Register your models here.
class InstaUserAdmin(admin.ModelAdmin):
    list_display = ["id","username","email","created_at"]
    search_fields = ["username","email"]
    list_display_links = ["username"]
    list_per_page = 10  
    list_filter = ["created_at"]
    list_order_by_desc = ["created_at"]


class instaPostAdmin(admin.ModelAdmin):
    list_display = ["id","caption"]


admin.site.register(instauser,InstaUserAdmin)
admin.site.register(instaPost)
admin.site.register(FollowUsers)
admin.site.register(notification)
admin.site.register(like_dislike)
admin.site.register(InstaReels)
admin.site.register(ChatRoom)
admin.site.register(Message)
admin.site.register(Comment)
admin.site.register(SearchHistory)
