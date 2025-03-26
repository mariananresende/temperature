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
import json

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
        pass  # vai continuar como None

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
    url = f"https://nominatim.openstreetmap.org/search?q={city_name}&format=json&limit=1"
    headers = {"User-Agent": "clima-com-ia"}
    response = requests.get(url, headers=headers)
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

# ========= Sessão do chat =========
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])

# ========= Entrada do usuário =========
user_input = st.chat_input("Pergunte a temperatura de qualquer cidade...")

if user_input:
    st.chat_message("user").markdown(user_input)

    # Prompt para decidir se é um pedido de clima
    city_decision_prompt = f"""
    Você é um assistente com acesso a funções. Aqui está uma função disponível:

    Função: consultar_temperatura(cidade: string)
    Descrição: Retorna a temperatura atual de uma cidade informada.

    O usuário escreveu: '{user_input}'

    Sua tarefa é decidir se deseja chamar a função 'consultar_temperatura'.

    Se for um pedido para saber a temperatura de uma cidade (ou apenas o nome da cidade), 
    retorne o seguinte JSON, com o nome real da cidade no campo "cidade":
    {{
      "chamar_funcao": true,
      "cidade": "Dublin"
    }}


    Se a frase não tiver relação com clima ou for sobre outros assuntos, 
    responda com este JSON:
    {{
      "chamar_funcao": false,
      "cidade": null
    }}

    Responda SOMENTE com o JSON. Sem explicações, sem markdown.
    """

    decision = model.generate_content(city_decision_prompt)

    try:
        # Remove crases, blocos de código e explicações do retorno do modelo
        raw_response = decision.text.strip()

        # Remove crases, blocos de markdown, e deixa só o JSON
        cleaned_response = raw_response.replace("```json", "").replace("```", "").strip()

        decision_json = json.loads(cleaned_response)



        if decision_json.get("chamar_funcao") and decision_json.get("cidade"):
            city_name = decision_json["cidade"]
            lat, lon = get_coordinates_from_city(city_name)

            if lat and lon:
                temp, desc, local_nome = get_weather_by_coordinates(lat, lon)
                if temp is not None:
                    resposta = model.generate_content(
                        f"A temperatura atual em {local_nome} é de {temp}°C com {desc}. "
                        f"Responda ao usuário de forma simpática e natural em português, como um assistente amigável."
                    )
                else:
                    resposta = model.generate_content(
                        f"A cidade {city_name} foi encontrada, mas o clima não pôde ser consultado. "
                        f"Peça desculpas e sugira tentar mais tarde."
                    )
            else:
                resposta = model.generate_content(
                    f"A cidade '{city_name}' não pôde ser localizada. "
                    f"Peça desculpas e oriente o usuário a verificar a grafia ou tentar outra cidade."
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




