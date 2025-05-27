import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# OpenRouter API settings
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
DEEPSEEK_MODEL = "deepseek/deepseek-chat-v3-0324:free"

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# System prompts for different languages
SYSTEM_PROMPTS = {
    "EN": """You are a professional support assistant. Your job is to enhance and rewrite any given message so it sounds clear, helpful, empathetic, and professional—without changing the core meaning. Always keep the tone customer-friendly, respectful, and supportive. Use correct grammar, structure, and polite language. Keep responses concise unless more detail is needed to clarify an issue. Do not add unrelated information or assumptions.

When enhancing the message:

Fix grammar and spelling

Use polite and empathetic phrasing

Maintain a calm, professional tone

Clarify technical terms if necessary (briefly)

Ensure the message is easy to understand

Output only the enhanced message without any explanation or preamble.""",
    "FR": """
Vous êtes un(e) assistant(e) professionnel(le). Votre tâche consiste à améliorer et à réécrire un message donné pour qu'il soit clair, utile, empathique et professionnel, sans en modifier le sens principal. Le ton doit toujours être convivial, respectueux et encourageant. Utilisez une grammaire et une structure correctes, ainsi qu'un langage poli. Les réponses doivent être concises, sauf si des détails supplémentaires sont nécessaires pour clarifier une question. N'ajoutez pas d'informations ou de suppositions sans rapport avec le sujet.

Lorsque vous améliorez le message :

Corrigez la grammaire et l'orthographe

Utilisez des formules de politesse et d'empathie.

Maintenir un ton calme et professionnel

Clarifier les termes techniques si nécessaire (brièvement)

Veiller à ce que le message soit facile à comprendre

Ne diffusez que le message amélioré, sans explication ni préambule."""
}

def generate_response(prompt, language):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "http://localhost:8501",
        "X-Title": "Customer Support Assistant",
        "Content-Type": "application/json"
    }

    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPTS[language]},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 1000,
    }

    try:
        response = requests.post(OPENROUTER_API_URL, headers=headers, json=payload)

        # Now try to parse as JSON
        response.raise_for_status()
        response_json = response.json()
        
        if "choices" not in response_json or not response_json["choices"]:
            st.error("No choices in response")
            return None
            
        return response_json["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        st.error(f"Request Error: {str(e)}")
        return None
    except ValueError as e:
        st.error(f"JSON Parsing Error: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Unexpected Error: {str(e)}")
        return None

# Streamlit UI
st.title("🤖 Customer Support Reply Generator")
st.caption("Bilingual Support Agent - FR/EN")

# Language selection
lang = st.selectbox("Select Language", ["EN", "FR"])

# Chat interface
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input and response generation
if prompt := st.chat_input("Enter your message"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate response
    with st.spinner("Generating message..."):
        full_response = generate_response(prompt, lang)
        
        if full_response:
            # Display assistant response
            with st.chat_message("assistant"):
                st.markdown(full_response)
            
            # Add to chat history
            st.session_state.messages.append({"role": "assistant", "content": full_response})