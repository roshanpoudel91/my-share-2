
from django.shortcuts import render, redirect
from django.views import View
from .forms import RegisterForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth import login, get_user_model
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponse
from django.conf import settings
from django.core.mail import send_mail
from finapp.models import UserMeta
import random
import string
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.sessions.models import Session
from django.utils import timezone
#---------TEST VIEW---------------
def test(request):
    return render(request,'home/test.html',{})
#----------END TEST VIEW-----------

# Create your views here.

class HomeView(View):
    def get(self, request):
        context={'user':request.user}
        return render(request, 'home/home.html',context)

def register_user(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration Successful.")
            return redirect(reverse('finapp:main_view'))
        messages.error(request, "Unsuccessful registration. Invalid information.")
        return render(request, 'registration/register.html',context={"form":form})
    form = RegisterForm()
    return render(request, 'registration/register.html',context={"form":form})


def my_login_view(request):
    if request.method != 'POST':
       return render(request, 'registration/login.html')
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is None:
            message = 'Invalid credentials'
            messages.error(request, message)
            return redirect(request.META.get('HTTP_REFERER'))
        #multiple user login session check is disabled for now. Will back after more research on it.
        '''userModel = get_user_model()
        LoggedInuser = userModel.objects.filter(email=username).values('id', 'email')
        active_sessions = Session.objects.filter(expire_date__gte=timezone.now())
        for session in active_sessions:
                session_data = session.get_decoded()
               # return HttpResponse(session_data)
                for item in LoggedInuser:
                    if item['id'] == int(session_data.get('_auth_user_id')):
                        message = 'Session already exists. Please logout from previous session and try again!'
                        messages.error(request, message)
                        return redirect(request.META.get('HTTP_REFERER'))
        '''
        login(request, user)
        return redirect(reverse('finapp:main_view'))
            
def password_reset(request):

    if request.method == "POST":
        customuser=get_user_model()
        form=PasswordResetForm(request.POST)
        if form.is_valid():
            email = request.POST.get("email")

            #if User.objects.filter(email=email).exists():
            if customuser.objects.filter(email=email).exists():
                #------------------------------------------------------------------------------------------------
                # CAUTION: For now, I've selected the first user from the queryset if we ran into multiple users
                # with same email address. We need to address this situation as soon as possible.
                #------------------------------------------------------------------------------------------------
                #user = User.objects.filter(email=email)[0]
                user=customuser.objects.get(email=email)
                letters = string.ascii_lowercase
                random_string = ''.join(random.choice(letters) for i in range(30))
                # UserMeta.objects.create(user=user,random_pass_string=random_string)

                #create or update user_meta table based on user_id
                UserMeta.objects.update_or_create(
                                    user=user,
                                    defaults={"random_pass_string": random_string},
                                )
                # send email
                # using mailtrap for testing send email. Later on, have to implement own email server in production.
                # To change email settings in settings.py change following parameters:
                # EMAIL_HOST,EMAIL_PORT, EMAIL_USE_SSL, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD

                send_mail(
                        "Password Reset for My Amazing Stocks",
                        message="",
                        html_message=f"Dear user,<br><br><p>A request to reset your password was made on My Amazing Stocks.<p>If you didn't initiate the request, you don't need to take any further action.</p></p> <p>You may reset your password by clicking this <a href='{settings.ALLOWED_HOSTS[0]}/home/set-password/?email={email}&q={random_string}'>link</a> to reset your password.</p> <p>Regards,</p><p>My Amazing Stock Team</p>",
                        from_email="admin@myamazingstocks.com",
                        recipient_list=[email],
                        fail_silently=False,
                )

            return render(request,'registration/password-reset-done.html',context={"next":"inbox"})

    form = PasswordResetForm()
    return render(request,'registration/password-reset.html',context={"form":form})


def set_password(request):
    message = ""
    customuser=get_user_model()
    if(request.method == "POST"):
        form = SetPasswordForm(request.POST)
        if form.is_valid() == False:
              return render(request, 'registration/set-password.html',context={"form":form})

        password1 = request.POST.get('password1')
        email = request.GET.get('email')
        random_string = request.GET.get('q')

        #user = User.objects.get(email=email)
        try:
            user=customuser.objects.get(email=email)
            query_string = user.usermeta.random_pass_string
        except:
            message = "Something went wrong. Please request new link from <a href='/home/password-reset'>forgot password</a> link!"   
            return render(request, 'registration/set-password.html',context={"form":form,"next":message})
           
        #checking if email and string matches to database's email and string
        if(random_string != query_string):
              message="Something went wrong. Please retry with link in the email."
              return render(request, 'registration/set-password.html',context={"form":form,"next":message})

         #change password
        user.set_password(password1)
        user.save()
        #delete user meta after password changed
        UserMeta.objects.filter(user=user).delete()
        return render(request,"registration/password-reset-done.html",context={"next":"done"})


    form = SetPasswordForm()
    context = {"form":form,"next":message}
    return render(request,'registration/set-password.html',context=context)
