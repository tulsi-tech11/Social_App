from django.db import models
import math
from django.utils import timezone

# Create your models here.
class instauser(models.Model):
    gender_choices = (
        ('male','Male'),
        ('female','Female'),
    )
    username = models.CharField(max_length=100,unique=True)
    email = models.EmailField(unique=True,null=True,blank=True)
    password = models.CharField(max_length=100, null=True, blank=True)
    profile_pic = models.FileField(upload_to='profile_pics/', blank=True, null=True)
    gender = models.CharField(max_length=10,choices=gender_choices,blank=True, null=True)
    fullname = models.CharField(max_length=100,blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    otp = models.PositiveIntegerField(default=987)
    otp_created_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username

class instaPost(models.Model):
    user = models.ForeignKey(instauser, on_delete=models.CASCADE)
    image = models.FileField(upload_to='posts/')
    caption = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    tagged_users = models.ManyToManyField(instauser,related_name="tagged_user", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.caption if self.caption else f"Post {self.id}"
    
    def whenpublished(self):
        now = timezone.now()
        diff = now-self.created_at

        if diff.days == 0 and diff.seconds >= 0 and diff.seconds < 60:
            seconds = diff.seconds
            if seconds == 1:
                return str(seconds) + "second ago"
            else:
                return str(seconds) + " seconds ago"
            
        if diff.days == 0 and diff.seconds >= 60 and diff.seconds < 3600 :
            minutes = math.floor(diff.seconds/60)
            if minutes == 1:
                return str(minutes) + " minute ago"
            else:
                return str(minutes) + " minutes ago"
            
        if diff.days == 0 and diff.seconds >= 3600 and diff.seconds < 86400 :
            hours = math.floor(diff.seconds/3600)
            if hours == 1:
                return str(hours) + " hour ago"
            else:
                return str(hours) + " hours ago"
            
        if diff.days >= 1 and diff.days < 30:
            days = diff.days
            if days == 1:
                return str(days) + " day ago"
            else:
                return str(days) + " days ago"
            
        if diff.days >= 30 and diff.days < 365:
            months = math.floor(diff.days/30)
            if months == 1:
                return str(months) + " month ago" 
            else:
                return str(months) + " months ago"
            
        if diff.days >= 365:
            years = math.floor(diff.days/365)
            if years == 1:
                return str(years) + " year ago"
            else:
                return str(years) + " years ago"

class FollowUsers(models.Model):
    following = models.ForeignKey(instauser,on_delete=models.CASCADE,related_name="following")
    following_person = models.ForeignKey(instauser,on_delete=models.CASCADE,related_name="following_person")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.following.fullname} - following {self.following_person.fullname}"

class notification(models.Model):
    NOTIFICATION_TYPE = (
        ('follow', 'Follow'),
        ('like', 'Like'),
        ('comment', 'Comments'),
    )

    sender = models.ForeignKey(instauser,on_delete=models.CASCADE,related_name="sender_notification")
    receiver = models.ForeignKey(instauser,on_delete=models.CASCADE,related_name="receiver_notification")
    message = models.TextField()
    notification_type = models.CharField(max_length=15,choices=NOTIFICATION_TYPE)
    post_fk = models.ForeignKey(instaPost,on_delete=models.CASCADE,related_name="post_fk",null=True,blank=True)
    read_status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def whenpublished(self):
        now = timezone.now()
        diff = now-self.created_at

        if diff.days == 0 and diff.seconds >= 0 and diff.seconds < 60:
            seconds = diff.seconds
            if seconds == 1:
                return str(seconds) + "second ago"
            else:
                return str(seconds) + " seconds ago"
            
        if diff.days == 0 and diff.seconds >= 60 and diff.seconds < 3600 :
            minutes = math.floor(diff.seconds/60)
            if minutes == 1:
                return str(minutes) + " minute ago"
            else:
                return str(minutes) + " minutes ago"
            
        if diff.days == 0 and diff.seconds >= 3600 and diff.seconds < 86400 :
            hours = math.floor(diff.seconds/3600)
            if hours == 1:
                return str(hours) + " hour ago"
            else:
                return str(hours) + " hours ago"
            
        if diff.days >= 1 and diff.days < 30:
            days = diff.days
            if days == 1:
                return str(days) + " day ago"
            else:
                return str(days) + " days ago"
            
        if diff.days >= 30 and diff.days < 365:
            months = math.floor(diff.days/30)
            if months == 1:
                return str(months) + " month ago" 
            else:
                return str(months) + " months ago"
            
        if diff.days >= 365:
            years = math.floor(diff.days/365)
            if years == 1:
                return str(years) + " year ago"
            else:
                return str(years) + " years ago"
    
    def __str__(self):
        return f"{self.sender.username} {self.message} {self.receiver.username}"

class InstaReels(models.Model):
    user = models.ForeignKey(instauser, on_delete=models.CASCADE)
    video = models.FileField(upload_to='InstaReels/')
    thumbnails = models.ImageField(upload_to='InstaReels_thumbnails/', blank=True, null=True)
    caption = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    tagged_users = models.ManyToManyField(instauser,related_name="tagged_post",blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
   
    def whenpublished(self):
        now = timezone.now()
        diff = now-self.created_at

        if diff.days == 0 and diff.seconds >= 0 and diff.seconds < 60:
            seconds = diff.seconds
            if seconds == 1:
                return str(seconds) + "second ago"
            else:
                return str(seconds) + " seconds ago"
            
        if diff.days == 0 and diff.seconds >= 60 and diff.seconds < 3600 :
            minutes = math.floor(diff.seconds/60)
            if minutes == 1:
                return str(minutes) + " minute ago"
            else:
                return str(minutes) + " minutes ago"
            
        if diff.days == 0 and diff.seconds >= 3600 and diff.seconds < 86400 :
            hours = math.floor(diff.seconds/3600)
            if hours == 1:
                return str(hours) + " hour ago"
            else:
                return str(hours) + " hours ago"
            
        if diff.days >= 1 and diff.days < 30:
            days = diff.days
            if days == 1:
                return str(days) + " day ago"
            else:
                return str(days) + " days ago"
            
        if diff.days >= 30 and diff.days < 365:
            months = math.floor(diff.days/30)
            if months == 1:
                return str(months) + " month ago" 
            else:
                return str(months) + " months ago"
            
        if diff.days >= 365:
            years = math.floor(diff.days/365)
            if years == 1:
                return str(years) + " year ago"
            else:
                return str(years) + " years ago"

    def __str__(self):
        return self.caption if self.caption else f"Reel {self.id}"

class like_dislike(models.Model):
    user_fk = models.ForeignKey(instauser, on_delete=models.CASCADE, related_name="liked_by")
    post_fk = models.ForeignKey(instaPost, on_delete=models.CASCADE, related_name="like_post")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_fk.username} liked {self.post_fk.id}"

class Comment(models.Model):
    user = models.ForeignKey(instauser, on_delete=models.CASCADE)
    post = models.ForeignKey(instaPost, on_delete=models.CASCADE, related_name="comments")
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} commented on {self.post.id}"

class SearchHistory(models.Model):
    user = models.ForeignKey(instauser, on_delete=models.CASCADE, related_name="search_history")
    searched_user = models.ForeignKey(instauser, on_delete=models.CASCADE, related_name="searched_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('user', 'searched_user')

    def __str__(self):
        return f"{self.user.username} searched for {self.searched_user.username}"

class ChatRoom(models.Model):
    sender = models.ForeignKey(instauser, on_delete=models.CASCADE, related_name="sender_chat")
    reciver = models.ForeignKey(instauser, on_delete=models.CASCADE, related_name="reciver_chat")
    created_at = models.DateTimeField(auto_now_add=True)

class Message(models.Model):
    chat_room = models.ForeignKey(ChatRoom,on_delete=models.CASCADE, related_name="messages")
    sender_id = models.ForeignKey(instauser,on_delete=models.CASCADE, related_name="senderby", null=True,blank=True )
    content = models.TextField(null=True, blank=True)
    image = models.FileField(upload_to="chat_images/", null=True, blank=True)
    video = models.FileField(upload_to="chat_videos/", null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.content}"
