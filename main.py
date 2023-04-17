#!/usr/bin/python3

from dotenv import load_dotenv
import requests, os

# --- load environment variables ---
load_dotenv()
API_KEY = os.getenv('API_KEY')

# --- load api variables ---
URL = 'https://babelfy.io/v1/disambiguate'

text = 'Yo envié a mis naves a pelear contra los hombres, no contra los elementos'
lang = 'es'
params = {
    'text': text,
    'lang': lang,
    'key': API_KEY,
}

r = requests.get(URL, params=params)
print(r.content)
