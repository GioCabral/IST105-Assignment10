import random
from datetime import datetime

import requests
from pymongo import MongoClient
from django.shortcuts import render

from .forms import ContinentForm

OPENWEATHER_API_KEY = "0b86c9fe4070a7e83b1baa5679561997"

MONGO_URI = "mongodb://172.31.73.12:27017"
MONGO_DB_NAME = "geo_weather"
MONGO_COLLECTION_NAME = "searches"

try:
    mongo_client = MongoClient(MONGO_URI)
    mongo_db = mongo_client[MONGO_DB_NAME]
    searches_collection = mongo_db[MONGO_COLLECTION_NAME]
except Exception:
    mongo_client = None
    searches_collection = None


def continent_form_view(request):
    if request.method == 'POST':
        form = ContinentForm(request.POST)
        if form.is_valid():
            continent = form.cleaned_data['continent']

            countries_url = f"https://restcountries.com/v3.1/region/{continent}"
            resp = requests.get(countries_url, timeout=10)

            if resp.status_code != 200:
                return render(request, 'continent_form.html', {
                    'form': form,
                    'error': 'Could not fetch countries from API.',
                })

            countries = resp.json()

            countries_with_capital = [c for c in countries if c.get('capital')]

            if len(countries_with_capital) > 5:
                sample = random.sample(countries_with_capital, 5)
            else:
                sample = countries_with_capital

            results = []

            for c in sample:
                country_name = c['name']['common']
                capital = c['capital'][0]

                weather_url = "https://api.openweathermap.org/data/2.5/weather"
                params = {
                    'q': capital,
                    'appid': OPENWEATHER_API_KEY,
                    'units': 'metric',
                }

                w_resp = requests.get(weather_url, params=params, timeout=10)
                if w_resp.status_code != 200:
                    continue

                w = w_resp.json()
                temp = w['main']['temp']
                description = w['weather'][0]['description']

                results.append({
                    'country': country_name,
                    'capital': capital,
                    'temperature': temp,
                    'description': description,
                })

            if searches_collection is not None:
                try:
                    searches_collection.insert_one({
                        'continent': continent,
                        'results': results,
                        'created_at': datetime.utcnow(),
                    })
                except Exception:
                    pass

            return render(request, 'search_results.html', {
                'continent': continent,
                'results': results,
            })
    else:
        form = ContinentForm()

    return render(request, 'continent_form.html', {'form': form})


def history_view(request):
    searches = []
    if searches_collection is not None:
        try:
            searches = list(
                searches_collection.find().sort('created_at', -1).limit(20)
            )
        except Exception:
            searches = []

    return render(request, 'history.html', {'searches': searches})
