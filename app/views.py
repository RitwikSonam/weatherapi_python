from django.shortcuts import render, redirect
import requests
from django.conf import settings
from app.forms import *
from django.http import HttpResponse, HttpResponseRedirect
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Profile, WeatherData


def home(request):
    return render(request, 'home.html')

def registration(request):
    uf = UserForm()
    pf = ProfileForm()
    
    if request.method == 'POST' and request.FILES:
        UFD = UserForm(request.POST)
        PFD = ProfileForm(request.POST, request.FILES)
        
        if UFD.is_valid() and PFD.is_valid():
            user = UFD.save(commit=False)
            password = UFD.cleaned_data['password']
            user.set_password(password)
            user.save()

            profile = PFD.save(commit=False)
            profile.profile_user = user
            profile.save()

            send_mail(
                'Registration Successful',
                'Thanks for registering. Your registration is successful.',
                settings.EMAIL_HOST_USER, # Use the email from settings
                [user.email],
                fail_silently=False
            )
            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('user_login')
        else:
            messages.error(request, 'Registration failed. Please correct the errors.')

    return render(request, 'registration.html', {'uf': uf, 'pf': pf})

def user_login(request):
    if request.method == 'POST':
        username = request.POST['un']
        password = request.POST['pw']
        user = authenticate(username=username, password=password)

        if user and user.is_active:
            login(request, user)
            messages.success(request, f'Welcome back, {username}!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'user_login.html')

@login_required
def user_logout(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')

@login_required
def profile_display(request):
    try:
        profile = Profile.objects.get(profile_user=request.user)
        return render(request, 'profile_display.html', {'user': request.user, 'profile': profile})
    except Profile.DoesNotExist:
        messages.error(request, 'Profile not found.')
        return redirect('home')

@login_required
def change_password(request):
    if request.method == 'POST':
        new_password = request.POST.get('password')
        if new_password:
            user = request.user
            user.set_password(new_password)
            user.save()
            messages.success(request, 'Your password has been changed successfully.')
            return redirect('profile_display')
        else:
            messages.error(request, 'Please provide a new password.')
    return render(request, 'change_password.html')

def reset_password(request):
    if request.method == 'POST':
        un = request.POST.get('un')
        pw = request.POST.get('pw')

        try:
            user = User.objects.get(username=un)
            user.set_password(pw)
            user.save()
            messages.success(request, 'Password reset is done successfully.')
            return redirect('user_login')
        except User.DoesNotExist:
            messages.error(request, f'User "{un}" is not present in my database.')

    return render(request, 'reset_password.html')

def fetch_weather_data(request):
    context = {}

    if request.method == 'POST':
        city_name = request.POST.get('city')
        api_key ='0ddac2f2a96230b519b9119dd73f6bce'
        url = f'http://api.openweathermap.org/data/2.5/weather?q={city_name}&units=metric&appid={api_key}'

        try:
            response = requests.get(url)
            response.raise_for_status()
            weather_data = response.json()

            if weather_data.get('cod') != 200:
                context['error_message'] = f"City '{city_name}' not found. Please try again."
            else:
                weather_info = {
                    'city': weather_data.get('name'),
                    'temperature': weather_data['main']['temp'],
                    'humidity': weather_data['main']['humidity'],
                    'description': weather_data['weather'][0]['description'],
                    'wind_speed': weather_data['wind']['speed'],
                    'pressure': weather_data['main']['pressure'],
                    'feels_like': weather_data['main']['feels_like'],
                }
                context['weather_data'] = weather_info

                if request.user.is_authenticated:
                    WeatherData.objects.create(
                        username=request.user,
                        city=weather_info['city'],
                        temperature=weather_info['temperature'],
                        humidity=weather_info['humidity'],
                        weather=weather_info['description'],
                        speed=weather_info['wind_speed']
                    )
        except requests.exceptions.RequestException as e:
            context['error_message'] = f"An error occurred: {e}"
        except (KeyError, IndexError):
            context['error_message'] = f"Could not retrieve data for '{city_name}'. Please check the city name and try again."

    return render(request, 'fetch_weather_data.html', context)
