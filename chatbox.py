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

        /* Bot Avatar Animation */
        @keyframes float {{
            0% {{ transform: translateY(0px) rotate(0deg); }}
            50% {{ transform: translateY(-20px) rotate(5deg); }}
            100% {{ transform: translateY(0px) rotate(0deg); }}
        }}

        .assistant-avatar {{
            animation: float 3s ease-in-out infinite;
            margin-right: 1.5rem;
            width: 60px;
            height: 60px;
            border-radius: 50%;
            box-shadow: 0 5px 15px rgba(78, 204, 163, 0.3);
        }}

        /* Message Alignment */
        .assistant-message {{
            display: flex;
            align-items: center;
            padding: 1rem 0;
        }}

        /* Mobile Responsive */
        @media (max-width: 768px) {{
            .assistant-avatar {{
                width: 45px;
                height: 45px;
                margin-right: 1rem;
            }}
            .main {{ padding: 0.5rem !important; }}
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
        }}

        /* Message Transition */
        .stChatMessage {{
            transition: all 0.3s ease;
            border-radius: 15px;
            background: rgba(255, 255, 255, 0.05) !important;
            backdrop-filter: blur(10px);
            margin: 1rem 0;
        }}
    </style>
    """, unsafe_allow_html=True)

# ======================
#  GROQ CLIENT SETUP
# ======================
def initialize_groq_client():
    try:
        return Groq(api_key=st.secrets["GROQ"]["API_KEY"])
    except KeyError:
        st.error("🔑 API Key Error! Configure secrets in `.streamlit/secrets.toml`")
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
        <div style="padding: 1rem; background: rgba(255,255,255,0.05); border-radius: 10px;">
            <strong style="color: #4ecca3;">{DEVELOPER}</strong><br>
            📧 {EMAIL}<br>
            [![LinkedIn](https://img.shields.io/badge/Profile-blue?logo=linkedin)]({LINKEDIN})<br>
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
    st.set_page_config(
        page_title="Groq AI Chatbox",
        page_icon="🤖",
        layout="centered",
        initial_sidebar_state="auto"
    )
    inject_custom_css()

    st.title("💬 Groq AI Chatbox")
    st.caption("Experience real-time AI conversations powered by Groq's LPU technology")

    client = initialize_groq_client()
    selected_model = render_sidebar()

    if "messages" not in st.session_state:
        st.session_state.messages = [{
            "role": "assistant",
            "content": "Hello! I'm your AI assistant. How can I help you today? 🌟"
        }]

    for message in st.session_state.messages:
        if message["role"] == "assistant":
            with st.chat_message("assistant"):
                st.markdown(f"""
                <div class="assistant-message">
                    <img src="{BOT_AVATAR}" class="assistant-avatar">
                    <div>{message["content"]}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            with st.chat_message("user", avatar="👤"):
                st.markdown(message["content"])

    if prompt := st.chat_input("Type your message..."):
        try:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user", avatar="👤"):
                st.markdown(prompt)

            with st.spinner("🧠 Processing..."):
                response = client.chat.completions.create(
                    messages=st.session_state.messages[-5:],
                    model=selected_model,
                    temperature=0.7,
                    stream=True
                )
                
                full_response = []
                message_container = st.empty()
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        full_response.append(chunk.choices[0].delta.content)
                        message_container.markdown(f"""
                        <div class="assistant-message">
                            <img src="{BOT_AVATAR}" class="assistant-avatar">
                            <div>{"".join(full_response)}</div>
                        </div>
                        """, unsafe_allow_html=True)
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "".join(full_response)
                })

        except Exception as e:
            st.error(f"⚠️ Error: {str(e)}")
            st.session_state.messages.pop()

if __name__ == "__main__":
    main()