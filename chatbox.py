import streamlit as st
from groq import Groq

# ======================
#  CONFIGURATION
# ======================
DEVELOPER = "Waqas Baloch"
EMAIL = "waqaskhosa99@gmail.com"
LINKEDIN = "https://www.linkedin.com/in/waqas-baloch"
GITHUB = "https://github.com/Waqas-Baloch99/AI-Chatbox"
BOT_AVATAR = "https://cdn-icons-png.flaticon.com/512/4712/4712035.png"
MODEL_OPTIONS = ["mixtral-8x7b-32768", "llama2-70b-4096"]

# ======================
#  CUSTOM CSS
# ======================
def inject_custom_css():
    st.markdown(f"""
    <style>
        /* Base Styles */
        .main {{
            background: linear-gradient(135deg, #1a1a2e, #16213e);
            color: #e6e6e6;
            max-width: 800px;
            margin: 0 auto;
            padding: 1rem !important;
            font-family: 'Segoe UI', sans-serif;
        }}

        /* Chat Messages */
        @keyframes slideIn {{
            0% {{ transform: translateY(20px); opacity: 0; }}
            100% {{ transform: translateY(0); opacity: 1; }}
        }}

        .stChatMessage {{
            animation: slideIn 0.3s ease-out;
            margin: 1rem 0;
            border-radius: 15px;
            background: rgba(255, 255, 255, 0.05) !important;
            backdrop-filter: blur(10px);
            padding: 1.5rem;
        }}

        /* Mobile Responsive */
        @media (max-width: 768px) {{
            .main {{
                padding: 0.5rem !important;
                max-width: 100%;
            }}
            .stChatFloatingInputContainer {{
                width: 95% !important;
                bottom: 10px;
            }}
            .stChatMessage {{
                padding: 1rem;
                margin: 0.5rem 0;
            }}
            [data-testid="stSidebar"] {{
                width: 240px !important;
            }}
            h1 {{ font-size: 1.5rem !important; }}
        }}

        /* Loading Animation */
        @keyframes pulse {{
            0% {{ opacity: 1; }}
            50% {{ opacity: 0.5; }}
            100% {{ opacity: 1; }}
        }}
        .stSpinner > div {{
            animation: pulse 1.5s infinite;
            border-color: #4ecca3 !important;
            border-top-color: transparent !important;
        }}

        /* Interactive Elements */
        button:hover {{ transform: translateY(-2px); transition: all 0.2s ease; }}
        .stTextInput input {{
            transition: all 0.3s ease;
            background: rgba(255, 255, 255, 0.1) !important;
        }}
        .stTextInput input:focus {{ box-shadow: 0 0 0 2px #4ecca3; }}

        /* Scrollbar */
        ::-webkit-scrollbar {{ width: 6px; }}
        ::-webkit-scrollbar-track {{ background: rgba(0,0,0,0.1); }}
        ::-webkit-scrollbar-thumb {{ background: #4ecca3; border-radius: 3px; }}
    </style>
    """, unsafe_allow_html=True)

# ======================
#  GROQ CLIENT SETUP
# ======================
def initialize_groq_client():
    try:
        return Groq(api_key=st.secrets["GROQ"]["API_KEY"])
    except KeyError:
        st.error("""
        🔑 API Key Error! Configure secrets:
        1. Create `.streamlit/secrets.toml`
        2. Add:
           [GROQ]
           API_KEY = "your-api-key"
        """)
        st.stop()
    except Exception as e:
        st.error(f"🚨 Initialization Error: {str(e)}")
        st.stop()

# ======================
#  SIDEBAR COMPONENT
# ======================
def render_sidebar():
    with st.sidebar:
        st.title("🧑💻 Developer Info")
        st.markdown(f"""
        <div style="color: #e6e6e6; padding: 1rem; 
                   background: rgba(255, 255, 255, 0.05); 
                   border-radius: 10px;">
            <strong>{DEVELOPER}</strong><br>
            📧 {EMAIL}<br>
            [![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-blue?logo=linkedin)]({LINKEDIN})<br>
            [![GitHub](https://img.shields.io/badge/Source_Code-black?logo=github)]({GITHUB})
        </div>
        """, unsafe_allow_html=True)

        st.divider()
        st.header("⚙️ Settings")
        return st.selectbox("Select AI Model", MODEL_OPTIONS, index=0)

# ======================
#  CHAT INTERFACE
# ======================
def main():
    # Initialize App
    st.set_page_config(
        page_title="Groq AI Chatbox",
        page_icon="🤖",
        layout="centered",
        initial_sidebar_state="auto"
    )
    inject_custom_css()

    st.title("💬 Groq AI Chatbox")
    st.caption("Experience real-time AI conversations powered by Groq's LPU technology")

    # Initialize Components
    client = initialize_groq_client()
    selected_model = render_sidebar()

    # Initialize Session State
    if "messages" not in st.session_state:
        st.session_state.messages = [{
            "role": "assistant",
            "content": "Hello! I'm your AI assistant. How can I help you today?"
        }]

    # Display Messages
    for message in st.session_state.messages:
        avatar = "👤" if message["role"] == "user" else BOT_AVATAR
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

    # Handle Input
    if prompt := st.chat_input("Type your message..."):
        try:
            # Add User Message
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user", avatar="👤"):
                st.markdown(prompt)

            # Generate Response
            with st.spinner("🧠 Processing..."):
                response = client.chat.completions.create(
                    messages=st.session_state.messages[-5:],
                    model=selected_model,
                    temperature=0.7,
                    stream=True
                )
                
                # Stream Response
                full_response = []
                message_container = st.empty()
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        full_response.append(chunk.choices[0].delta.content)
                        message_container.markdown("".join(full_response))
                
                # Add Final Response
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "".join(full_response)
                })

        except Exception as e:
            st.error(f"⚠️ Error: {str(e)}")
            st.session_state.messages.pop()

if __name__ == "__main__":
    main()