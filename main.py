import streamlit as st
import requests, hashlib
import json, time

# User management
def load_users():
    try:
        # Load users from Streamlit secrets
        users = st.secrets["users"]
        return users
    except Exception as e:
        st.error("Error loading users configuration")
        return {}

def verify_user(username, password):
    users = load_users()
    if username in users:
        stored_hash = users[username]
        input_hash = hashlib.sha256(password.encode()).hexdigest()
        return stored_hash == input_hash
    return False

def generate_token(username):
    # Generate a simple token with username and timestamp
    timestamp = int(time.time())
    token_data = {
        "username": username,
        "timestamp": timestamp
    }
    return json.dumps(token_data)

def verify_token(token):
    try:
        token_data = json.loads(token)
        # Check if token is less than 24 hours old
        if time.time() - token_data["timestamp"] > 86400:  # 24 hours in seconds
            return None
        return token_data["username"]
    except:
        return None

# OpenRouter API settings
OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
DEEPSEEK_MODEL = "deepseek/deepseek-chat-v3-0324:free"

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None

# Check for existing token in query params
if "token" in st.query_params:
    token = st.query_params["token"]
    username = verify_token(token)
    if username:
        st.session_state.authenticated = True
        st.session_state.current_user = username

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

# Authentication function
def check_password():
    if not st.session_state.authenticated:
        st.title("🔒 Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            if verify_user(username, password):
                st.session_state.authenticated = True
                st.session_state.current_user = username
                # Generate and store token
                token = generate_token(username)
                # Set token in query params
                st.query_params["token"] = token
                st.rerun()
            else:
                st.error("Invalid username or password")
        return False
    return True

# Main app
if check_password():
    st.title("🤖 Customer Support Reply Generator")
    st.caption(f"Bilingual Support Agent - FR/EN | Logged in as: {st.session_state.current_user}")
    
    # Add logout button
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.current_user = None
        # Clear token from query params
        st.query_params.clear()
        st.rerun()

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