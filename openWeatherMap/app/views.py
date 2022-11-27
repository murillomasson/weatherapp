from django.shortcuts import render
import requests
import json
from datetime import datetime

API_KEY = 'e264f9ab41b21d92ca4296b6b38aa1f4'
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

            total = ', '.join([date, temperature, weather_main])

        context = {
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