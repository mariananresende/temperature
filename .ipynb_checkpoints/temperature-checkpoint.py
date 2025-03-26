#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# !pip install streamlit requests google-generativeai python-dotenv

import streamlit as st
import requests
import os
from dotenv import load_dotenv
import google.generativeai as genai


# In[ ]:


# Carrega as variáveis de ambiente
load_dotenv()

# Configura as APIs
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# Função para obter a temperatura via OpenWeather
def get_temperature(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=pt"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        temp = data["main"]["temp"]
        description = data["weather"][0]["description"]
        return temp, description
    else:
        return None, None

# LLM conversacional
model = genai.GenerativeModel("gemini-1.5-flash")

st.set_page_config("Consulta de Temperatura com IA 🌡️")
st.title("🌍 Clima com IA")
st.markdown("Pergunte a temperatura de qualquer cidade do mundo:")

# Histórico
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_input = st.chat_input("Ex: Qual a temperatura em Lisboa?")

if user_input:
    st.chat_message("user").markdown(user_input)
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    # Tenta extrair o nome da cidade da pergunta
    city_response = model.generate_content(f"A seguinte frase é uma pergunta sobre clima: '{user_input}'. Qual é a cidade mencionada?")
    city_name = city_response.text.strip()

    temp, desc = get_temperature(city_name)

    if temp is not None:
        resposta_llm = model.generate_content(
            f"O usuário perguntou sobre o clima em {city_name}. A temperatura atual é de {temp}°C com {desc}. Responda de forma natural e simpática em português."
        )
    else:
        resposta_llm = model.generate_content(
            f"O usuário perguntou sobre o clima em '{city_name}', mas essa cidade não foi encontrada na base de dados. Dê uma resposta educada em português explicando isso."
        )

    st.chat_message("assistant").markdown(resposta_llm.text)
    st.session_state.chat_history.append({"role": "assistant", "content": resposta_llm.text})

