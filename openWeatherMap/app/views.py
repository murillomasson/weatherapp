import json
from datetime import datetime
import requests
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

from .forms import UserForm, CityForm
from .models import City

API_KEY = ''
lang = 'pt_br'


def index(request):
    if request.method == 'POST':
        city = request.POST['city']
        geolocation = json.loads(
            requests.get(
                f"https://api.openweathermap.org/geo/1.0/direct?q={city}&limit=5&appid={API_KEY}&lang={lang}"
            ).text
        )
        lat = str(geolocation[0]['lat'])
        lon = str(geolocation[0]['lon'])
        source = json.loads(
            requests.get(
                f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}"
                f"&appid={API_KEY}&lang={lang}&units=metric"
            ).text
        )
        current_date = ''
        today = datetime.today()
        now = datetime.now().strftime("%H:%M")
        total = {}
        for item in source['list']:
            time = item['dt_txt']
            next_date, hour = time.split(' ')
            hour = f'{int(hour[:2])}h'

            temp = item['main']['temp']
            temperature = f'{temp}ºC'
            weather_main = str(item['weather'][0]['description'])
            weather_icon = item['weather'][0]['icon']

            if current_date != next_date:
                current_date = next_date
                y, m, d = current_date.split('-')
                date = f'{d}/{m}/{y}'

            total[date] = (temperature, weather_main)

        context = {
            "city": city,
            "date": date,
            "temp": temp,
            "total": total,
            "today": today,
            "now": now,
            "date": date,
            "temperature": temperature,
            "weather_main": weather_main,
            "weather_icon": weather_icon,
            "hour": hour,
            "current_temp": str(source['list'][0]['main']['temp']),
            "current_humidity": str(source['list'][0]['main']['humidity']),
            "current_feels_like": str(source['list'][0]['main']['feels_like']),
            "current_weather_main": str(source['list'][0]['weather'][0]['description']),
            "current_weather_icon": source['list'][0]['weather'][0]['icon'],
        }
    else:
        context = {}

    return render(request, "main/index.html", context)


def registeruser(request):
    if request.method == 'POST':
        uname = request.POST['username']
        em = request.POST['email']
        pass1 = request.POST['password1']
        pass2 = request.POST['password2']
        form = UserForm()
        if pass1 == pass2:
            if User.objects.filter(username=uname).exists():
                return render(request, 'main/register.html', {'form': form, 'error': 'Username already taken'})
            else:
                if User.objects.filter(email=em).exists():
                    return render(request, 'main/register.html', {'form': form, 'error': 'Email-id already taken'})
                else:
                    user = User.objects.create_user(username=uname, email=em, password=pass1)
                    user.save()
                    return redirect('login_user')
        else:
            return render(request, "main/register.html", {'form': form, 'error': 'Password not matching'})
    else:
        form = UserForm()
        return render(request, 'main/register.html', {'form': form})


def loginuser(request):
    if request.method == 'GET':
        return render(request, 'main/login.html', {'form': AuthenticationForm()})
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'main/login.html',
                          {'form': AuthenticationForm(), 'error': 'username and password did not match'})
        else:
            login(request, user)
            return redirect('main')


@login_required
def logoutuser(request):
    logout(request)
    return redirect('')


@login_required
def logoutuser(request):
	logout(request)
	return redirect('')
@login_required
def mainpage(request):
    flag = False
    url = 'http://api.openweathermap.org/data/2.5/' \
          'weather?q={}&units=metric&appid=2a5035a1a9287c44491f251ad0719454&lang=pt_br'
    cities = City.objects.all()
    weather_data = []
    ex_weather_data = []
    form = CityForm()
    message = ''
    if request.method == 'POST':
        if 'city' in request.POST:
            form = CityForm(request.POST)
            if form.is_valid():
                temp = form.cleaned_data['name'].capitalize()
                x = City.objects.filter(name=temp).count()
                cod = requests.get(url.format(temp)).json()['cod']
                if x == 0 and cod != '404':
                    c = City(name=temp)
                    c.save()
                    request.user.city.add(c)
                elif x != 0:
                    for c in request.user.city.all():
                        if temp == c.name:
                            message = 'cidade já adicionada'
                            flag = True
                    if not flag:
                        c = City(name=temp)
                        c.save()
                        request.user.city.add(c)
                elif cod == '400':
                    message = 'cidade inválida'
    if request.user.is_authenticated:
        for city in cities:
            if city in request.user.city.all():
                city_weather = requests.get(url.format(city)).json()
                weather = {
                    'city': str(city).capitalize(),
                    'temperature': city_weather['main']['temp'],
                    'description': city_weather['weather'][0]['description'],
                    'icon': city_weather['weather'][0]['icon']
                }
                weather_data.append(weather)
                ex_weather = {
                    'city': str(city).capitalize(),
                    'temperature': city_weather['main']['temp'],
                    'feels_like': city_weather['main']['feels_like'],
                    'pressure': city_weather['main']['pressure'],
                    'humidity': city_weather['main']['humidity'],
                    'description': city_weather['weather'][0]['description'],
                    'icon': city_weather['weather'][0]['icon'],
                    'wind_speed': city_weather['wind']['speed']
                }
                ex_weather_data.append(ex_weather)
    context = {
        'weather_data': weather_data,
        'ex_weather_data': ex_weather_data,
        'form': form,
        'messages': message,
    }
    return render(request, 'main/main.html', context)
@login_required
def delete(request, name):
    request.user.city.all().filter(name=name).delete()
    return redirect('main')
