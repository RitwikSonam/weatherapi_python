
from app.forms import *
from django.http import HttpResponse,HttpResponseRedirect
from django.core.mail import send_mail
from django.contrib.auth import authenticate,login,logout
from django.urls import reverse
from django.contrib.auth.decorators import login_required
import requests
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import UserUpdateForm, ProfileUpdateForm
from django.contrib import messages
from django.contrib.auth.models import User

def home(request):
    if request.session.get('username'):
        username=request.session.get('username')
        d={'username':username}
        return render(request,'home.html',d)
    return render(request,'home.html')

def registration(request):
    uf=UserForm()
    pf=ProfileForm()
    d={'uf':uf,'pf':pf}

    if request.method=='POST' and request.FILES:
        UFD=UserForm(request.POST)
        PFD=ProfileForm(request.POST,request.FILES)
        if UFD.is_valid() and PFD.is_valid():
            UFO=UFD.save(commit=False)
            password=UFD.cleaned_data['password']
            UFO.set_password(password)
            UFO.save()

            PFO=PFD.save(commit=False)
            PFO.profile_user=UFO
            PFO.save()

            send_mail('registration',
            'Thanks for registartion,ur registration is Successfull',
            'ritwiksonam1@gmail.com',
            [UFO.email],
            fail_silently=False
            
            )
            return HttpResponse('registration is succeffull')


    return render(request,'registration.html',d)

def user_login(request):
    if request.method=='POST':
        username=request.POST['un']
        password=request.POST['pw']
        user=authenticate(username=username,password=password)

        if user and user.is_active:
            login(request,user)
            request.session['username']=username
            return HttpResponseRedirect(reverse('home'))
        else:
            return HttpResponse('u r not an authenticated user')
    return render(request,'user_login.html')



@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('home'))

@login_required
def profile_display(request):
    un=request.session.get('username')
    UO=User.objects.get(username=un)
    PO=Profile.objects.get(profile_user=UO)
    d={'UO':UO,'PO':PO}
    return render(request,'profile_display.html',d)

@login_required
def change_password(request):

    if request.method=='POST':
        pw=request.POST['password']

        un=request.session.get('username')
        UO=User.objects.get(username=un)

        UO.set_password(pw)
        UO.save()
        return HttpResponse('password is changed successfully')

    return render(request,'change_password.html')


def reset_password(request):

    if request.method=='POST':
        un=request.POST['un']
        pw=request.POST['pw']

        LUO=User.objects.filter(username=un)

        if LUO:
            UO=LUO[0]
            UO.set_password(pw)
            UO.save()
            return HttpResponse('password reset is done')
        else:
            return HttpResponse('user is not present in my DB')
        

        return HttpResponse('Reset password is done successfully')
    return render(request,'reset_password.html')





@login_required
def search(request):
    if request.method=='POST':
        city_name=request.POST['city']
        api_key = '30d4741c779ba94c470ca1f63045390a'
        url = f'http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}'
        response = requests.get(url)
        weather_data = response.json()
        print(weather_data)
        temperature = weather_data['main']['temp'] - 273.15
        humidity = weather_data['main']['humidity']
        weather=weather_data['main']['feels_like'] - 273.15
        speed=weather_data['wind']['speed']
        username=request.session.get('username')
        LUO=User.objects.get(username=username)
        obj=WeatherData.objects.get_or_create(username=LUO,city=city_name, temperature=round (temperature, 2), humidity=humidity,weather=round(weather, 2), speed=speed)[0]
        obj.save()
        d={'obj':obj}
        return render(request,'search.html',d)
    
    return render(request,'search.html')



@login_required
def user_history(request):
    username=request.session['username']
    UO=User.objects.get(username=username)
    LWO=WeatherData.objects.filter(username=UO)

    d={'LWO':LWO}
    return render(request,'user_history.html',d)


def all_history(request):
    LWO=WeatherData.objects.all()
    d={'LWO':LWO}
    return render(request,'user_history.html',d)

@login_required
def edit_profile(request):
    if request.method == 'POST':
        uf = UserUpdateForm(request.POST, instance=request.user)
        pf = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if uf.is_valid() and pf.is_valid():
            uf.save()
            pf.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile_display')
    else:
        uf = UserUpdateForm(instance=request.user)
        pf = ProfileUpdateForm(instance=request.user.profile)

    return render(request, 'edit_profile.html', {'uf': uf, 'pf': pf})



@login_required
def delete_profile(request):
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, 'Your profile has been deleted.')
        return redirect('home')
    return render(request, 'delete_confirm.html')


from django.http import JsonResponse
import requests

def get_weather(request):
    lat = request.GET.get('lat')
    lon = request.GET.get('lon')
    if not lat or not lon:
        return JsonResponse({'error': 'Missing coordinates'}, status=400)

    try:
        # Replace with your actual weather API call
        url = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid=YOUR_API_KEY&units=metric'
        response = requests.get(url)
        data = response.json()
        return JsonResponse({
            'weather': data['weather'][0]['main'],
            'temperature': data['main']['temp']
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)






















































