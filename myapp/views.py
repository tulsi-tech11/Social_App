from django.core.mail import send_mail
from django.conf import settings as django_settings
from myapp.models import instauser
from django.shortcuts import render,redirect
from django.http import HttpResponseRedirect, JsonResponse
from .models import *
from django.contrib.auth.hashers import make_password,check_password
from .utils import customeSendMail,get_or_create_chatRoom
import random
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta

def checklogin(view_function):
    def wrapper(request,*args,**kwargs):
        if "email" in request.session:
            try:
                uid = instauser.objects.get(email = request.session['email'])
                request.uid = uid
                return view_function(request,*args,**kwargs)
            except instauser.DoesNotExist:
                return redirect("login")
        return redirect("login")
    return wrapper

def login(request):
    if request.POST:
        email = request.POST['email']
        password =request.POST['password']

        try:
            uid = instauser.objects.get(email = email)
            if not check_password(password,uid.password):
                context = {
                    'e_msg' : "Invalid Credentials !"
                }
                return render(request,"myapp/login.html",context)
            else:
                request.session['email'] = email 
                context = {
                     'uid' : uid 
                }
                return redirect("home")

        except:
            context = {
                'e_msg' : "User Not Found !"
            }
            return render(request,"myapp/login.html",context)

    return render(request,'myapp/login.html')

def register(request):
    if request.POST:
        username = request.POST['username']
        email = request.POST['email']
        gender = request.POST['gender']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if instauser.objects.filter(username=username).exists():
            context = {
                'e_msg' : "Username Already exists !"
            }
            return render(request,"myapp/register.html",context)

        elif instauser.objects.filter(email = email).exists():
            context = {
                'e_msg' : "Email Already exists !"
            }
            return render(request,"myapp/register.html",context)

        elif password!= confirm_password:
            context = {
                'e_msg': "Password does not match !"
            }
            return render(request,"myapp/register.html",context)

        else:
            img = None

            gender_lower = gender.lower()
            if gender_lower == "male":
                img = "images/boy.png"
            elif gender_lower == "female":
                img = "images/girl.png"

            instauser.objects.create(
                    username = username,
                    email = email,
                    password = make_password(password),
                    profile_pic = img,
                    gender = gender
                    )
                    
            return redirect("login")

    return render(request,"myapp/register.html")


def logout(request):
    if "email" in request.session:
        del request.session['email']
        return redirect("login")
    return redirect("login")

@checklogin   
def edit_profile(request):
    uid = request.uid

    if request.POST:
        uid.fullname = request.POST['fullname']
        uid.username = request.POST['username']
        uid.bio = request.POST['bio']
        uid.description = request.POST['description']
        uid.link = request.POST['link']

        if 'profile_pic' in request.FILES:
            uid.profile_pic = request.FILES['profile_pic']

        uid.save()
        return redirect("profile")
    
    context = {
        'uid': uid,
    }
    return render(request, "myapp/edit_profile.html", context)

@checklogin 
def create(request):
    uid = request.uid

    if request.POST:
        image = request.FILES['image']
        caption = request.POST['caption']
        location = request.POST['location']

        instaPost.objects.create(
            user=uid,
            image=image,
            caption=caption,
            location=location
        )

        return redirect("home")

    context = {
        'uid': uid,
    }
    return render(request, "myapp/create.html", context)


@checklogin
def home(request):
    uid = request.uid
    
    my_following_ids = FollowUsers.objects.filter(following=uid).values_list("following_person_id", flat=True)
    post_all = instaPost.objects.filter(user__in=list(my_following_ids)).order_by('-created_at')
    suggestions = instauser.objects.exclude(id__in=list(my_following_ids)).exclude(id=uid.id)

    liked_post_ids = set(like_dislike.objects.filter(user_fk=uid).values_list('post_fk_id', flat=True))

    video_extensions = ('.mp4', '.webm', '.ogg', '.mov')
    for post in post_all:
        post.is_liked = post.id in liked_post_ids
        post.is_video = post.image.name.lower().endswith(video_extensions)
        post.post_comments = post.comments.all().order_by('-created_at')[:2]
        post.comment_count = post.comments.count()

    context = {
        'uid': uid,
        'post_all': post_all,
        'suggestions': suggestions,
    }
    return render(request, "myapp/home.html", context)


@checklogin
def add_comment(request, pk):
    uid = request.uid
    if request.method == "POST":
        try:
            post_obj = instaPost.objects.get(id=pk)
            text = request.POST.get('comment')
            
            if text:
                comment = Comment.objects.create(
                    user=uid,
                    post=post_obj,
                    text=text
                )
                
                if post_obj.user != uid:
                    notification.objects.create(
                        sender=uid,
                        receiver=post_obj.user,
                        message=f'commented: "{text}"',
                        notification_type="comment",
                        post_fk=post_obj
                    )

                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({
                        'status': 'success',
                        'username': uid.username,
                        'text': text,
                        'comment_count': post_obj.comments.count()
                    })
        except instaPost.DoesNotExist:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': 'Post not found'}, status=404)

    return redirect('home')


@checklogin
def get_comments(request, pk):
    try:
        post_obj = instaPost.objects.get(id=pk)
        comments = post_obj.comments.all().order_by('-created_at')
        comments_data = []
        for c in comments:
            comments_data.append({
                'username': c.user.username,
                'profile_pic': c.user.profile_pic.url if c.user.profile_pic else '/static/images/default_user.png',
                'text': c.text,
                'created_at': c.created_at.strftime("%b %d, %Y")
            })
        return JsonResponse({'status': 'success', 'comments': comments_data})
    except instaPost.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Post not found'}, status=404)


@checklogin
def profile(request):
    uid = request.uid
    mypost = instaPost.objects.filter(user=uid).order_by('-created_at')
    count_post = instaPost.objects.filter(user = uid).count
    count_follower = FollowUsers.objects.filter(following_person = uid).count()
    count_following = FollowUsers.objects.filter(following = uid).count()

    context = {
        'uid': uid,
        'mypost': mypost,
        'count_follower': count_follower,
        'count_following' : count_following,
        'count_post': count_post
    }
    return render(request, "myapp/profile.html", context)

@checklogin
def search(request):
    uid = request.uid
    query = request.GET.get('q')
    results = None
    
    if query:
        results = instauser.objects.filter(
            Q(username__icontains=query) | Q(fullname__icontains=query)
        ).exclude(id=uid.id)
    
    recent_searches = SearchHistory.objects.filter(user=uid).order_by('-created_at')[:5]
    trending_posts = instaPost.objects.all().order_by('-created_at')[:9]

    context = {
        'uid': uid,
        'query': query,
        'results': results,
        'recent_searches': recent_searches,
        'trending_posts': trending_posts
    }
    return render(request, "myapp/search.html", context)


@checklogin
def add_to_search_history(request, pk):
    uid = request.uid
    target_user = instauser.objects.get(id=pk)
    
    history_obj, created = SearchHistory.objects.get_or_create(user=uid, searched_user=target_user)
    if not created:
        history_obj.created_at = timezone.now()
        history_obj.save()
    
    return redirect('user_profile', pk=pk)

@checklogin
def user_profile(request, pk):
    uid = request.uid
    
    if pk == uid.id:
        return redirect('profile')

    try:
        target_user = instauser.objects.get(id=pk)
    except instauser.DoesNotExist:
        return redirect('search')

    user_posts = instaPost.objects.filter(user=target_user).order_by('-created_at')
    count_post = instaPost.objects.filter(user=target_user).count()
    count_follower = FollowUsers.objects.filter(following_person=target_user).count()
    count_following = FollowUsers.objects.filter(following=target_user).count()
    is_following = FollowUsers.objects.filter(following=uid, following_person=target_user).exists()

    context = {
        'uid': uid,
        'target_user': target_user,
        'user_posts': user_posts,
        'count_post': count_post,
        'count_follower': count_follower,
        'count_following': count_following,
        'is_following': is_following
    }
    return render(request, "myapp/user_profile.html", context)


@checklogin
def delete_search_history(request, pk):
    uid = request.uid
    SearchHistory.objects.filter(user=uid, id=pk).delete()
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    return redirect('search')

@checklogin
def settings(request):
    uid = request.uid
    context = {
        'uid': uid,
    }
    return render(request,"myapp/settings.html", context)

@checklogin
def following(request):
    uid = request.uid
    users = instauser.objects.exclude(username=uid.username)
    my_following = FollowUsers.objects.filter(following=uid).values_list('following_person_id', flat=True)
    
    search = request.GET.get("search")
    if search:
        users = users.filter(
            Q(username__icontains = search) |
            Q(fullname__icontains = search)
        )

    context = {
        'uid': uid,
        'users': users,
        'my_following': my_following,
    }
    return render(request, "myapp/following.html", context)


@checklogin
def follow_unfollow(request, pk):
    uid = request.uid
    try:
        target_user = instauser.objects.get(id=pk)
    except instauser.DoesNotExist:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': 'User not found'}, status=404)
        return redirect('home')

    following_person = FollowUsers.objects.filter(
        following=uid,
        following_person=target_user).first()
    
    if following_person:
        following_person.delete()
        notification.objects.filter(
            sender=uid,
            receiver=target_user,
            notification_type="follow"
        ).delete()
        status = 'unfollowed'
    else:
        FollowUsers.objects.create(
            following=uid,
            following_person=target_user
        )
        
        notification.objects.create(
            sender=uid,
            receiver=target_user,
            message="started following you..",
            notification_type="follow"
        )
        status = 'followed'
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'follow_status': status})

    referer = request.META.get('HTTP_REFERER', '/')
    return redirect(referer)
    

@checklogin
def followers(request):
    uid = request.uid
    followers_list = FollowUsers.objects.filter(following_person=uid).select_related('following')
    my_following = FollowUsers.objects.filter(following=uid).values_list('following_person_id', flat=True)

    search = request.GET.get("search")
    if search:
        followers_list = followers_list.filter(
            Q(following__username__icontains=search) |
            Q(following__fullname__icontains=search)
        )

    context = {
        'uid': uid,
        'followers_list': followers_list,
        'my_following': my_following,   
    }
    return render(request, "myapp/followers.html", context)

@checklogin
def remove(request,pk):
    uid = request.uid
    FollowUsers.objects.filter(following_id=pk, following_person=uid).delete()
    return redirect("followers")


@checklogin
def notification_view(request):
    uid = request.uid
    notifications = notification.objects.filter(receiver=uid).order_by('-created_at')
    notification.objects.filter(receiver=uid, read_status=False).update(read_status=True)
    my_following = FollowUsers.objects.filter(following = uid).values_list("following_person",flat=True)

    context = {
        'uid': uid,
        'notifications' :  notifications,
        'my_following' : my_following
    }
    return render(request,"myapp/notifications.html",context)


@checklogin
def like_dislike_view(request, pk):
    uid = request.uid
    try:
        post_obj = instaPost.objects.get(id=pk)
    except instaPost.DoesNotExist:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': 'Post not found'}, status=404)
        return redirect('home')

    likes_queryset = like_dislike.objects.filter(user_fk=uid, post_fk=post_obj)

    if likes_queryset.exists():
        likes_queryset.delete()
        liked = False
        if post_obj.user != uid:
            notification.objects.filter(
                sender=uid,
                receiver=post_obj.user,
                notification_type="like",
                post_fk=post_obj
            ).delete()
    else:
        like_dislike.objects.create(user_fk=uid, post_fk=post_obj)
        liked = True
        if post_obj.user != uid:
            notification.objects.create(
                sender=uid,
                receiver=post_obj.user,
                message="liked your post",
                notification_type="like",
                post_fk=post_obj
            )

    like_count = like_dislike.objects.filter(post_fk=post_obj).count()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'liked': liked,
            'like_count': like_count
        })

    return redirect('home')

@checklogin
def create_reel(request):
    uid = request.uid
    if request.POST:
        video = request.FILES['video']
        caption = request.POST['caption']
        location = request.POST['location']
        InstaReels.objects.create(
            user=uid,
            video=video,
            caption=caption,
            location = location
        )
        return redirect("home")
    context = { 'uid': uid }
    return render(request, "myapp/create_reel.html", context)


@checklogin
def reels(request):
    uid = request.uid
    all_reels = InstaReels.objects.all().order_by('-created_at')
    context = {
        'uid': uid,
        'all_reels': all_reels
    }
    return render(request, "myapp/reels.html", context)
    

def forgot_password(request):
    if request.POST:
        email = request.POST.get('email', '').strip()
        uid = instauser.objects.filter(email__iexact=email).first()
        if uid:
            otp = random.randint(100000, 999999)
            uid.otp = otp
            uid.save()
            try:
                send_mail(
                    subject="Password Reset OTP",
                    message=f"Your OTP for password reset is: {otp}",
                    from_email=django_settings.EMAIL_HOST_USER,
                    recipient_list=[email],
                    fail_silently=False,
                )
            except Exception as e:
                print("Failed to send email:", e)
                return render(request, "myapp/forgot_password.html", {'e_msg': f"Failed to send email: {str(e)}"})
            return render(request, "myapp/verify_otp.html",{'email':email})
        else:
            return render(request, "myapp/forgot_password.html",{'e_msg' : "User does not exist.!!!"})
    return render(request, "myapp/forgot_password.html")


def verify_otp(request): 
    if request.method == "POST":
        email = request.POST.get('email', '').strip()
        otp = request.POST.get('otp', '').strip()
        uid = instauser.objects.filter(email__iexact=email).first()
        if uid and str(uid.otp) == otp:
            return render(request, "myapp/reset_password.html", {'email': email})
        else:
            return render(request, "myapp/verify_otp.html", {'email': email, 'e_msg': 'Invalid OTP'})
    return redirect("forgot_password")


def reset_password(request):
    if request.POST:
        email = request.POST.get('email', '').strip()
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        uid = instauser.objects.filter(email__iexact=email).first()
        if uid:
            if new_password == confirm_password:
                uid.password = make_password(new_password)
                uid.save()
                return redirect("login")
            else:
                return render(request, "myapp/reset_password.html", {'email': email, 'e_msg': 'Passwords do not match'})
        else:
            return redirect("forgot_password")
    return render(request, "myapp/reset_password.html")


@checklogin
def messages(request, pk=None):
    uid = request.uid
    following_list = FollowUsers.objects.filter(following=uid)
    chat_list = []
    
    for f in following_list:
        person = f.following_person
        room = ChatRoom.objects.filter(
            (Q(sender=uid) & Q(reciver=person)) | (Q(sender=person) & Q(reciver=uid))
        ).first()
        unread_count = 0
        last_msg_preview = "Click to chat"
        if room:
            unread_count = Message.objects.filter(chat_room=room, is_read=False).exclude(sender_id=uid).count()
            last_msg_obj = Message.objects.filter(chat_room=room).order_by('-created_at').first()
            if last_msg_obj:
                last_msg_preview = last_msg_obj.content if last_msg_obj.content else "Sent a file"
        chat_list.append({'user': person, 'unread_count': unread_count, 'last_msg': last_msg_preview})

    receiver = None
    messages = None
    if pk:
        receiver = instauser.objects.get(id=pk)
        room = get_or_create_chatRoom(uid, receiver)
        messages = Message.objects.filter(chat_room=room).order_by('created_at')
        Message.objects.filter(chat_room=room, is_read=False).exclude(sender_id=uid).update(is_read=True)

    context = {
        'uid': uid,
        'chat_list': chat_list,
        'receiver': receiver,
        'messages': messages
    }
    return render(request, "myapp/messages.html", context)


@checklogin
def send_msg(request, pk):
    if request.POST:
        uid = request.uid
        sender = instauser.objects.get(id=uid.id)
        receiver = instauser.objects.get(id=pk)
        conversation_room = get_or_create_chatRoom(sender, receiver)
        content = request.POST['message']
        msg_obj = Message.objects.create(
            chat_room=conversation_room,
            sender_id=sender,
            content=content,
        )
        if "image" in request.FILES:
            msg_obj.image = request.FILES['image']
            msg_obj.save()
        if "video" in request.FILES:
            msg_obj.video = request.FILES['video']
            msg_obj.save()
        return redirect("messages",pk=receiver.id)

@checklogin
def get_unread_counts(request):
    uid = request.uid
    unread_notifications = notification.objects.filter(receiver=uid, read_status=False).count()
    unread_messages = Message.objects.filter(
        chat_room__in=ChatRoom.objects.filter(Q(sender=uid) | Q(reciver=uid)),
        is_read=False
    ).exclude(sender_id=uid).count()

    return JsonResponse({
        'notifications': unread_notifications,
        'messages': unread_messages
    })

