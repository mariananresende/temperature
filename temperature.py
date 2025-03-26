#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# !pip install streamlit requests google-generativeai python-dotenv

import streamlit as st
import requests
import os
import pandas as pd  # <- adicione aqui
from dotenv import load_dotenv
import google.generativeai as genai


# In[ ]:


# Carrega as variáveis de ambiente
load_dotenv()

# Tenta pegar da nuvem, se não existir, pega do .env (uso local)
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
WEATHER_API_KEY = st.secrets.get("WEATHER_API_KEY") or os.getenv("WEATHER_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)


st.set_page_config(page_title="Clima com IA", page_icon="🌍")
st.title("🌤️ Consulta de Temperatura com IA")

# ========= Função: Extrai coordenadas com Nominatim =========
def get_coordinates_from_city(city_name):
    url = f"https://nominatim.openstreetmap.org/search?q={city_name}&format=json&limit=1"
    headers = {"User-Agent": "clima-com-ia"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200 and response.json():
        data = response.json()[0]
        return float(data["lat"]), float(data["lon"])
    return None, None

# ========= Função: Consulta clima real por coordenadas =========
def get_weather_by_coordinates(lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric&lang=pt"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data["main"]["temp"], data["weather"][0]["description"], data["name"]
    return None, None, None

# ========= Modelo Gemini =========
model = genai.GenerativeModel("gemini-1.5-flash")

# ========= Histórico =========
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])

# ========= Interface =========
user_input = st.chat_input("Pergunte a temperatura de qualquer cidade...")

if user_input:
    st.chat_message("user").markdown(user_input)

    # Extrair o nome da cidade com Gemini
    city_resp = model.generate_content(
        f"Na frase: '{user_input}', qual é a cidade mencionada? Responda apenas com o nome da cidade, sem frases ou pontuação."
    )
    city_name = city_resp.text.strip()

    lat, lon = get_coordinates_from_city(city_name)

    if lat and lon:
        temp, desc, local_nome = get_weather_by_coordinates(lat, lon)
        if temp is not None:
            # Gerar resposta natural com Gemini
            resposta = model.generate_content(
                f"A temperatura atual em {local_nome} é de {temp}°C com {desc}. Responda ao usuário de forma simpática e natural em português, como um assistente amigável."
            )
        else:
            resposta = model.generate_content(
                f"A cidade {city_name} foi encontrada, mas o clima não pôde ser consultado. Peça desculpas e sugira tentar mais tarde."
            )
    else:
        resposta = model.generate_content(
            f"A cidade '{city_name}' não pôde ser localizada. Peça desculpas e oriente o usuário a verificar a grafia ou tentar outra cidade."
        )

    st.chat_message("assistant").markdown(resposta.text)
    st.map(pd.DataFrame({"lat": [lat], "lon": [lon]}))

