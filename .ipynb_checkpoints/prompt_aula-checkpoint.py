#!/usr/bin/env python
# coding: utf-8

# In[1]:


#!pip install streamlit


# In[2]:


get_ipython().system('pip install -q google-generativeai')


# In[3]:


#streamlit python llm
import streamlit as st
from pathlib import Path
import google.generativeai as genai


# In[4]:


#config
genai.configure(api_key="AIzaSyC6DYCw3byrbdtwNLqLbq6osQvyRXIYlDM")


# In[5]:


# prompt: escrever um prompt para uma sistema avançado de IA de análise de imagens médicas para ser colocado no system_prompt. Inclua questões médicas e dê mais exemplos de resultados de imagens

system_prompt = """
Você é um especialista em análise de imagens médicas com amplo conhecimento em radiologia, anatomia e fisiologia.
Sua tarefa é analisar imagens médicas fornecidas pelo usuário e responder a perguntas relacionadas à imagem, fornecendo insights clínicos relevantes.

**Seu objetivo é fornecer respostas precisas, completas e concisas com base na imagem e nos conhecimentos médicos relevantes.**

**Exemplos de perguntas que você pode responder:**

* "O que está acontecendo nesta imagem de raio-x de tórax?"
* "Existe alguma anormalidade nesta imagem de ressonância magnética do cérebro?"
* "Qual é a provável causa desta lesão na imagem de ultrassom abdominal?"
* "Esta imagem de tomografia computadorizada do abdome revela alguma evidência de hemorragia?"
* "Quais são as possíveis consequências dessa imagem de radiografia de membro inferior?"

**Exemplo de formato de resposta:**

**Imagem:** [Tipo de Imagem] (Ex: Raio-x de tórax)
**Descrição:** [Encontrar achados relevantes, como opacidades, derrame pleural, etc.]
**Diagnóstico:** [Diagnóstico ou Diagnósticos diferenciais, ex: Pneumonia, Derrame pleural]
**Comentários:** [Informações adicionais, como severidade, gravidade ou qualquer outra observação relevante.]

**Exemplos de resultados da imagem:**

* **Raio-x de tórax:**
    * Derrame pleural à direita:  Ocorre um acúmulo de fluidos no espaço pleural.
    * Opacidade na base pulmonar esquerda: Pode indicar pneumonia, atelectasia ou derrame pleural.
    * Massa pulmonar: Pode ser um tumor ou infecção.
* **Ressonância magnética do cérebro:**
    * Massa na região frontal: Pode indicar um tumor ou infecção.
    * Hemorragia subaracnóidea: Uma hemorragia que envolve o espaço entre o cérebro e a membrana que o envolve.
* **Ultrassom abdominal:**
    * Cálculos biliares: Pedras na vesícula biliar.
    * Massa hepática: Pode indicar um tumor ou cisto.
* **Tomografia computadorizada do abdome:**
    * Apendicite: inflamação do apêndice.
    * Diverticulite: inflamação de uma pequena bolsa no intestino grosso.
* **Radiografia de membro inferior:**
    * Fratura de fêmur: quebra no fêmur.
    * Luxação de joelho: a junta do joelho está fora do lugar.

**Lembre-se de sempre referenciar os achados da imagem para apoiar suas respostas e diagnośticos.**

**Seu papel é fornecer uma análise clínica detalhada e profunda sobre as imagens fornecidas.**
"""

geenration_config={
    "temperature":1,
    "top_k":40,
    "top_p":0.95,
    "max_output_tokens":8192,
    "response_mine_type":"text/plain",
}

safety_seetings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE",
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE",
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE",
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE",
    },
]


#layout

st.set_page_config(page_title="Análise diagnóstica",page_icon=":robot")
col1,col2,col3=st.columns([1,2,1])#center
with col2:
    st.image("edureka.png",width=200)
    st.image("medical.jpeg",width=200)

upload_file=st.file_uploader("Carregue as imagens médicas",type=["png","jpg","jpeg"])
submit_button=st.button("Análise da imagem")

if submit_button:
  #process the uploaded image
  image_data=upload_file.getvalue()

  #making our image ready
  image_parts = [
      {
          "mime_type": "image/jpeg",
          "content": image_data,
      }
  ]
  #making our prompt ready
  prompt_parts=[
      image_parts[0],
      system_prompt,
  ]
  #generate a response based on prompt and image
  response = model.generate_content(prompt_parts)
  print(response.text)

  st.write(response.text)



# In[25]:


# prompt: como rodar o streamlit para executar o código para gerar a análise da imagem médica. Onde está o terminal

import streamlit as st
from pathlib import Path
import google.generativeai as genai
# !pip install streamlit  # Uncomment if you need to install streamlit

# Streamlit configuration
st.set_page_config(page_title="Análise diagnóstica", page_icon=":robot:")

# Configuration
genai.configure(api_key="AIzaSyC6DYCw3byrbdtwNLqLbq6osQvyRXIYlDM")  # Replace with your API key

system_prompt = """
... (Your system prompt code) ...
"""

generation_config = {
    "temperature": 1,
    "top_k": 40,
    "top_p": 0.95,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE",
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE",
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE",
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE",
    },
]

# Layout
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("edureka.png", width=200)
    st.image("medical.jpeg", width=200)

upload_file = st.file_uploader("Carregue as imagens médicas", type=["png", "jpg", "jpeg"])
submit_button = st.button("Análise da imagem")

if submit_button and upload_file is not None:
  # Process the uploaded image
  image_data = upload_file.getvalue()

  # Making our image ready
  image_parts = [
      {
          "mime_type": "image/jpeg",
          "content": image_data,
      }
  ]

  # Making our prompt ready
  prompt_parts = [
      image_parts[0],
      system_prompt,
  ]

  # Generate a response based on prompt and image
  model = genai.DiscussModel()  # Choose the appropriate model for image analysis
  response = model.generate_message(prompt=prompt_parts, examples=[], generation_config=generation_config)
  print(response.candidates[0]["content"])

  st.write(response.candidates[0]["content"])



# In[27]:




