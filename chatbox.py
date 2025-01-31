import os
import streamlit as st
from groq import Groq
from dotenv import load_dotenv

# ========== DEVELOPER CONFIG ========== #
DEVELOPER_INFO = {
    "name": "Waqas Baloch",
    "email": "waqaskhosa99@gmail.com",
    "linkedin": "https://www.linkedin.com/in/waqas-baloch",
    "github": "https://github.com/Waqas-Baloch99/AI-Chatbox"
}

# ========== APP CONFIGURATION ========== #
load_dotenv()
MODELS = {
    "🚀 Mixtral-8x7b": "mixtral-8x7b-32768",
    "🦙 LLaMA2-70b": "llama2-70b-4096"
}

# ========== CUSTOM STYLES ========== #
def inject_custom_css():
    st.markdown(f"""
    <style>
        .main {{
            max-width: 800px;
            padding: 2rem;
        }}
        .stChatInput {{
            position: fixed;
            bottom: 20px;
            width: 65%;
        }}
        .stMarkdown {{
            line-height: 1.6;
        }}
        .developer-info {{
            padding: 1rem;
            background: #f8f9fa;
            border-radius: 10px;
            margin-bottom: 2rem;
        }}
        [data-testid="stSidebar"] {{
            width: 350px !important;
        }}
    </style>
    """, unsafe_allow_html=True)

# ========== CORE FUNCTIONS ========== #
def initialize_groq_client():
    """Initialize Groq client with fail-safe"""
    api_key = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ.API_KEY")
    if not api_key:
        st.error("🔑 API key not found. Please configure your credentials.")
        st.stop()
    return Groq(api_key=api_key)

def render_sidebar():
    """Sidebar with developer info and controls"""
    with st.sidebar:
        st.title("⚙️ Controls")
        selected_model = st.selectbox(
            "Select AI Model",
            options=list(MODELS.keys()),
            index=0,
            help="Choose between different AI models"
        )
        
        st.divider()
        with st.container():
            st.subheader("🧑💻 Developer Info")
            st.markdown(f"""
            <div class="developer-info">
                <strong>{DEVELOPER_INFO['name']}</strong><br>
                📧 {DEVELOPER_INFO['email']}<br>
                [![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-blue?logo=linkedin)]({DEVELOPER_INFO['linkedin']})<br>
                [![GitHub](https://img.shields.io/badge/Source_Code-black?logo=github)]({DEVELOPER_INFO['github']})
            </div>
            """, unsafe_allow_html=True)
            
    return MODELS[selected_model]

def handle_chat_interaction(client, model):
    """Handle chat messages with optimized rendering"""
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display existing messages
    for msg in st.session_state.messages:
        avatar = "👤" if msg["role"] == "user" else "🤖"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

    # Handle new input
    if prompt := st.chat_input("Type your message..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        # Generate response
        with st.chat_message("assistant", avatar="🤖"):
            try:
                response = client.chat.completions.create(
                    messages=st.session_state.messages[-10:],  # Keep last 10 messages
                    model=model,
                    temperature=0.7,
                    max_tokens=1024
                ).choices[0].message.content
                
                # Stream response for better UX
                response_container = st.empty()
                full_response = ""
                for chunk in response.split():
                    full_response += chunk + " "
                    response_container.markdown(full_response + "▌")
                response_container.markdown(full_response)
                
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
            except Exception as e:
                st.error(f"⚠️ Error generating response: {str(e)}")

# ========== MAIN APP ========== #
def main():
    st.set_page_config(
        page_title="Groq Chatbox",
        page_icon="🤖",
        layout="centered",
        initial_sidebar_state="expanded"
    )
    inject_custom_css()
    
    st.title("💬 Groq AI Chatbox")
    st.caption("Experience real-time AI conversations powered by Groq's LPU technology")
    
    client = initialize_groq_client()
    selected_model = render_sidebar()
    handle_chat_interaction(client, selected_model)

if __name__ == "__main__":
    main()