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

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

if not GEMINI_API_KEY or not WEATHER_API_KEY:
    try:
        GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
        WEATHER_API_KEY = st.secrets["WEATHER_API_KEY"]
    except (FileNotFoundError, KeyError):
        pass

if not GEMINI_API_KEY or not WEATHER_API_KEY:
    st.error("⚠️ API keys não foram encontradas. Verifique o .env ou o secrets.toml.")
    st.stop()

# ========= Funções =========
def get_coordinates_from_city(city_name):
    url_full = f"https://nominatim.openstreetmap.org/search?q={city_name}&format=json&limit=1&addressdetails=1"
    headers = {"User-Agent": "clima-com-ia"}
    response = requests.get(url_full, headers=headers)

    if response.status_code == 200 and response.json():
        data = response.json()[0]
        return float(data["lat"]), float(data["lon"])

    city_only = city_name.split(",")[0]
    url_simple = f"https://nominatim.openstreetmap.org/search?q={city_only}&format=json&limit=1&addressdetails=1"
    response = requests.get(url_simple, headers=headers)

    if response.status_code == 200 and response.json():
        data = response.json()[0]
        return float(data["lat"]), float(data["lon"])

    return None, None

def get_weather_by_coordinates(lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric&lang=pt"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data["main"]["temp"], data["weather"][0]["description"], data["name"]
    return None, None, None

def consultar_temperatura(local: str) -> dict:
    lat, lon = get_coordinates_from_city(local)
    if lat and lon:
        temp, desc, nome = get_weather_by_coordinates(lat, lon)
        if temp is not None:
            return {"mensagem": f"A temperatura atual em {nome} é de {temp} °C com {desc}.", "lat": lat, "lon": lon}
        else:
            return {"mensagem": f"A cidade {local} foi encontrada, mas o clima não pôde ser consultado.", "lat": None, "lon": None}
    return {"mensagem": f"A cidade '{local}' não foi localizada.", "lat": None, "lon": None}

# ========= Configura modelo com ferramentas =========
genai.configure(api_key=GEMINI_API_KEY)

functions = [
    {
        "name": "consultar_temperatura",
        "description": "Obtém a temperatura atual de uma cidade com base no nome da localidade.",
        "parameters": {
            "type": "object",
            "properties": {
                "local": {
                    "type": "string",
                    "description": "Nome da cidade (pode incluir o país, ex: 'Lisbon, Portugal')"
                }
            },
            "required": ["local"]
        }
    }
]

model = genai.GenerativeModel("gemini-1.5-flash", tools=[{"function_declarations": functions}])

# ========= Interface =========
st.set_page_config(page_title="Clima com IA", page_icon="🌍")
st.title("🌤️ Consulta de Temperatura com IA")

if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])

user_input = st.chat_input("Pergunte a temperatura de qualquer cidade...")

if user_input:
    st.chat_message("user").markdown(user_input)
    response = st.session_state.chat.send_message(user_input, stream=False)

    # DEBUG opcional (log bruto da resposta)
    # st.write(response)

    # Executa a função chamada se houver
    try:
        call = response.candidates[0].content.parts[0].function_call
        if call.name == "consultar_temperatura":
            result = consultar_temperatura(**call.args)
            st.chat_message("function").markdown(result["mensagem"])
            if result["lat"] and result["lon"]:
                st.map(pd.DataFrame({"lat": [result["lat"]], "lon": [result["lon"]]}))
    except Exception as e:
        st.write("Erro ao interpretar function_call:", e)

    # Renderiza resposta textual, se houver
    try:
        parts = response.candidates[0].content.parts
        reply = "".join([part.text for part in parts if hasattr(part, "text")])
        if reply.strip():
            st.chat_message("assistant").markdown(reply)
    except Exception as e:
        st.write("Erro ao extrair resposta de texto:", e)







