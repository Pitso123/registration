from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import ClassSchedule
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib import messages
from django.views import View
from django.conf import settings

# Your existing view
def LandingPage(request):
    return render(request, 'index.html')


@login_required(login_url='login')
def HomePage(request):
    return render(request, 'home.html')
 

def SignupPage(request):
    if request.method == 'POST':
        uname = request.POST.get('username')
        email = request.POST.get('email')
        pass1 = request.POST.get('password1')
        pass2 = request.POST.get('password2')

        if pass1 != pass2:
            return HttpResponse("Your password and confirm password are not the same!!")
        else:
            my_user = User.objects.create_user(uname, email, pass1)
            my_user.save()
            return redirect('login')
    
    return render(request, 'signup.html')

def LoginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        pass1 = request.POST.get('pass')
        user = authenticate(request, username=username, password=pass1)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return HttpResponse("Username or Password is incorrect!!!")

    return render(request, 'login.html')

def LogoutPage(request):
    logout(request)
    return redirect('index')

# Class schedule views
def schedule_view(request):
    schedules = ClassSchedule.objects.filter(user=request.user)
    return render(request, 'schedule.html', {'schedules': schedules})

@login_required
def add_schedule(request):
    if request.method == "POST":
        course_name = request.POST['course_name']
        instructor = request.POST['instructor']
        day = request.POST['day']
        time = request.POST['time']
        discussion = request.POST.get('discussion', '')

        schedule = ClassSchedule.objects.create(
            user=request.user,
            course_name=course_name,
            instructor=instructor,
            day=day,
            time=time,
            discussion=discussion
        )
        return JsonResponse({"message": "Schedule added!", "id": schedule.id})

@login_required
def delete_schedule(request, schedule_id):
    schedule = ClassSchedule.objects.get(id=schedule_id, user=request.user)
    schedule.delete()
    return JsonResponse({"message": "Schedule deleted!"})

# Password reset views
class ForgotPasswordView(View):
    def get(self, request):
        return render(request, 'forgot_password.html')
    
    def post(self, request):
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            
            # Generate token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Create reset link
            reset_link = request.build_absolute_uri(
                f'/reset-password/{uid}/{token}/'
            )
            
            # Send email
            send_mail(
                'Password Reset Request',
                f'Click the link to reset your password: {reset_link}\n\n'
                f'If you didn\'t request this, please ignore this email.',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            
            messages.success(request, 'Password reset link has been sent to your email.')
            return redirect('forgot_password')
            
        except User.DoesNotExist:
            messages.error(request, 'No user with that email address exists.')
            return redirect('forgot_password')

class ResetPasswordView(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            
            if default_token_generator.check_token(user, token):
                return render(request, 'reset_password.html', {
                    'uidb64': uidb64,
                    'token': token
                })
            else:
                messages.error(request, 'Invalid or expired reset link.')
                return redirect('login')
                
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            messages.error(request, 'Invalid reset link.')
            return redirect('login')
    
    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            
            if default_token_generator.check_token(user, token):
                new_password1 = request.POST.get('new_password1')
                new_password2 = request.POST.get('new_password2')
                
                if new_password1 != new_password2:
                    messages.error(request, 'Passwords do not match.')
                    return render(request, 'reset_password.html', {
                        'uidb64': uidb64,
                        'token': token
                    })
                
                if len(new_password1) < 8:
                    messages.error(request, 'Password must be at least 8 characters.')
                    return render(request, 'reset_password.html', {
                        'uidb64': uidb64,
                        'token': token
                    })
                
                user.set_password(new_password1)
                user.save()
                messages.success(request, 'Your password has been reset successfully. You can now login with your new password.')
                return redirect('login')
            else:
                messages.error(request, 'Invalid or expired reset link.')
                return redirect('login')
                
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            messages.error(request, 'Invalid reset link.')
            return redirect('login')