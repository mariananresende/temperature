import streamlit as st
from pathlib import Path
import google.generativeai as genai

#  Deve ser o primeiro comando do Streamlit
st.set_page_config(page_title="Análise diagnóstica", page_icon=":robot:")
st.title("Análise de Imagens Médicas com IA")


#config

import os
from dotenv import load_dotenv

load_dotenv()  # Carrega as variáveis do arquivo .env

api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)


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

generation_config={
    "temperature":1,
    "top_k":40,
    "top_p":0.95,
    "max_output_tokens":8192,
    "response_mime_type":"text/plain",
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


#layout

col1,col2,col3 = st.columns([1,2,1])#center
with col2:
    st.image("edureka.png",width=200)
    st.image("medical.jpeg",width=200)

upload_file=st.file_uploader("Carregue as imagens médicas",type=["png","jpg","jpeg"])
submit_button=st.button("Análise da imagem")

if "resultado_analise" not in st.session_state:
    st.session_state.image_analysis_result = None

if "chat" not in st.session_state:
    st.session_state.chat = None

if submit_button and upload_file is not None:
    image_data = upload_file.getvalue()

    image_part = {
        "inline_data": {
            "mime_type": "image/jpeg",
            "data": image_data,
        }
    }

    prompt_parts = [
        image_part,
        {"text": system_prompt}
    ]

    #model = genai.GenerativeModel(model_name="gemini-1.5-flash")

    #response = model.generate_content(
     #   prompt_parts,
      #  generation_config=generation_config,
     #   safety_settings=safety_settings
   # )

   # 

    model = genai.GenerativeModel(model_name="gemini-1.5-pro")

    response = model.generate_content(
        prompt_parts,
        generation_config=generation_config,
        safety_settings=safety_settings
    )

    
    st.session_state.resultado_analise = response.text

    st.markdown("### Resultado da análise da imagem:")
    st.write(response.text)


# --------------------------Chat com GPT---------------------------


    st.session_state.chat = model.start_chat(
        history=[
            {
                "role": "user",
                "parts": [f"Esta foi a análise da imagem médica:\n\n{response.text}"],
            },
            {
                "role": "model",
                "parts": ["Estou pronto para responder perguntas sobre essa análise."],
            },
        ]
    )
    
if st.session_state.get("resultado_analise"):
    st.divider()
    st.subheader("💬 Chat com a IA sobre o resultado")

    user_question = st.chat_input("Pergunte algo sobre o diagnóstico...")

    if user_question:
        st.chat_message("user").markdown(user_question)
        chat_response = st.session_state.chat.send_message(user_question)
        st.chat_message("assistant").markdown(chat_response.text)
else:
    st.info("🧪 Primeiro envie uma imagem médica para análise.")







