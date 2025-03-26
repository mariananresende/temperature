#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# !pip install streamlit requests google-generativeai python-dotenv

import streamlit as st
import requests
import os
import pandas as pd
from dotenv import load_dotenv
import google.generativeai as genai

# ========= Carrega variáveis de ambiente =========
load_dotenv()

# Primeiro tenta pegar do .env
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

# Se não encontrar no .env, tenta no secrets (Streamlit Cloud)
if not GEMINI_API_KEY or not WEATHER_API_KEY:
    try:
        GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
        WEATHER_API_KEY = st.secrets["WEATHER_API_KEY"]
    except (FileNotFoundError, KeyError):
        pass

# Validação básica
if not GEMINI_API_KEY or not WEATHER_API_KEY:
    st.error("⚠️ API keys não foram encontradas. Verifique o arquivo .env (modo local) ou secrets.toml (Streamlit Cloud).")
    st.stop()

# ========= Configura modelo =========
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# ========= Configuração da página =========
st.set_page_config(page_title="Clima com IA", page_icon="🌍")
st.title("🌤️ Consulta de Temperatura com IA")

# ========= Função: Extrai coordenadas com Nominatim =========
def get_coordinates_from_city(city_name):
    # Tenta primeiro com o nome completo (ex: "Salvador, Brazil")
    url_full = f"https://nominatim.openstreetmap.org/search?q={city_name}&format=json&limit=1&addressdetails=1"
    headers = {"User-Agent": "clima-com-ia"}
    response = requests.get(url_full, headers=headers)

    if response.status_code == 200 and response.json():
        data = response.json()[0]
        return float(data["lat"]), float(data["lon"])

    # Se não funcionar, tenta apenas a cidade (ex: "Salvador")
    city_only = city_name.split(",")[0]
    url_simple = f"https://nominatim.openstreetmap.org/search?q={city_only}&format=json&limit=1&addressdetails=1"
    response = requests.get(url_simple, headers=headers)

    if response.status_code == 200 and response.json():
        data = response.json()[0]
        return float(data["lat"]), float(data["lon"])

    return None, None


# ========= Função: Consulta clima por coordenadas =========
def get_weather_by_coordinates(lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric&lang=pt"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data["main"]["temp"], data["weather"][0]["description"], data["name"]
    return None, None, None

# ========= Função real que será chamada com base no modelo =========
def consultar_temperatura(local):
    lat, lon = get_coordinates_from_city(local)
    if lat and lon:
        temp, desc, nome = get_weather_by_coordinates(lat, lon)
        if temp is not None:
            return f"A temperatura atual em {nome} é de {temp}°C com {desc}.", lat, lon
        else:
            return f"A cidade {local} foi encontrada, mas o clima não pôde ser consultado. Tente mais tarde.", None, None
    else:
        return f"A cidade '{local}' não pôde ser localizada. Verifique a grafia ou tente outra cidade.", None, None

# ========= Sessão do chat =========
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])

# ========= Entrada do usuário =========
user_input = st.chat_input("Pergunte a temperatura de qualquer cidade...")

if user_input:
    st.chat_message("user").markdown(user_input)

    # Prompt para extrair a localidade
    extract_location_prompt = f"""
    O usuário escreveu: '{user_input}'

    Extraia apenas o nome do local (cidade ou cidade + país) que aparece na frase, se houver.

    Responda apenas com o nome do local no formato: "Cidade, País", com o país em inglês, como por exemplo: "Salvador, Brazil", "Lisbon, Portugal".

    Se não houver local, responda apenas com: "none"
    """

    try:
        location_result = model.generate_content(extract_location_prompt)
        local = location_result.text.strip().replace('"', '').replace('Brasil', 'Brazil')

        if local.lower() != "none":
            resultado, lat, lon = consultar_temperatura(local)
            resposta = model.generate_content(
                f"{resultado} Responda ao usuário de forma simpática e natural em português, como um assistente amigável."
            )
        else:
            resposta_texto = (
                "Desculpe! Sou um assistente especializado em clima. "
                "Você pode me perguntar, por exemplo: 'Qual a temperatura em Lisboa?' 🌍"
            )

    except Exception as e:
        resposta = model.generate_content(
            f"Houve um erro ao interpretar a solicitação: {str(e)}. Peça desculpas e oriente o usuário a tentar novamente."
        )

    # Renderização da resposta
    if "resposta" in locals():
        st.chat_message("assistant").markdown(resposta.text)
    elif "resposta_texto" in locals():
        st.chat_message("assistant").markdown(resposta_texto)

    # Mostra o mapa se houver coordenadas válidas
    if 'lat' in locals() and lat and lon:
        st.map(pd.DataFrame({"lat": [lat], "lon": [lon]}))
