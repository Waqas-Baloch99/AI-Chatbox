import streamlit as st
from groq import Groq
import time

DEVELOPER = "Waqas Baloch"
BOT_AVATAR = "https://cdn-icons-png.flaticon.com/512/4712/4712035.png"
MODEL_INFO = {
    "mixtral-8x7b-32768": "High-quality text generation with 8 experts mixture",
    "llama-3.3-70b-versatile": "Large 70B parameter model for complex tasks",
    "deepseek-r1-distill-llama-70b-specdec": "Optimized 32B parameter model for fast, high-quality responses"
}

def inject_custom_css():
    st.markdown("""
    <style>
        :root {
            --primary-color: #00ddeb;
            --secondary-color: #7b00ff;
            --bg-gradient: linear-gradient(145deg, #0f172a, #1e293b);
            --card-bg: rgba(255, 255, 255, 0.05);
            --shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        }

        .main {
            background: var(--bg-gradient);
            min-height: 100vh;
            color: #f1f5f9;
            padding: 2rem;
            font-family: 'Inter', sans-serif;
        }

        .assistant-message {
            display: flex;
            align-items: center;
            gap: 1rem;
            padding: 1.5rem;
            background: var(--card-bg);
            border-radius: 20px;
            margin: 1rem 0;
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: var(--shadow);
            animation: slideUp 0.4s ease-out;
        }

        .assistant-avatar {
            width: 48px;
            height: 48px;
            border-radius: 50%;
            border: 2px solid var(--primary-color);
            object-fit: cover;
            animation: shake 1.5s infinite ease-in-out;
        }

        .message-content {
            flex: 1;
        }

        .response-time {
            font-size: 0.75rem;
            color: var(--primary-color);
            opacity: 0.8;
            margin-top: 0.5rem;
        }

        @media (max-width: 768px) {
            .assistant-message { padding: 1rem; }
            .assistant-avatar { width: 36px; height: 36px; }
        }

        @keyframes slideUp {
            from { transform: translateY(20px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }

        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            25% { transform: translateX(-3px); }
            75% { transform: translateX(3px); }
        }
    </style>
    """, unsafe_allow_html=True)

def get_api_key():
    try:
        return st.secrets["GROQ"]["API_KEY"]
    except:
        st.error("Error accessing API key: Please ensure secrets.toml has [GROQ] section with API_KEY")
        return None

def main():
    st.set_page_config(page_title="AI Chatbox", page_icon="🤖", layout="wide")
    inject_custom_css()

    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("<h1 style='color: #fff; margin-bottom: 0;'>🤖 AI Chatbox</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color: #94a3b8;'>Powered by Groq's cutting-edge LPU technology</p>", unsafe_allow_html=True)

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "response_times" not in st.session_state:
        st.session_state.response_times = []

    with st.sidebar:
        st.markdown("<h2 style='color: #fff;'>⚙️ Control Panel</h2>", unsafe_allow_html=True)
        selected_model = st.selectbox(
            "Select AI Model",
            list(MODEL_INFO.keys()),
            format_func=lambda x: f"{x} - {MODEL_INFO[x]}",
            help="Choose your preferred AI model"
        )

        if st.button("Clear Conversation", key="clear", use_container_width=True):
            st.session_state.messages = []
            st.session_state.response_times = []
            st.rerun()

        st.markdown("---")
        st.markdown(f"""
        <div style='text-align: center; color: #94a3b8; font-size: 1.1rem; padding: 1rem;'>
            <h3 style='color: var(--primary-color); margin-bottom: 0.5rem;'>Developed by {DEVELOPER}</h3>
            <div style='margin-top: 1rem;'>
                <p><a href="mailto:waqaskhos99@gmail.com" style='color: var(--primary-color); text-decoration: none;'><span style='margin-right: 0.5rem;'>📧</span> waqaskhos99@gmail.com</a></p>
                <p><a href="https://www.linkedin.com/in/waqas-baloch" style='color: var(--primary-color); text-decoration: none;'><span style='margin-right: 0.5rem;'>🔗</span> LinkedIn</a></p>
                <p><a href="https://github.com/Waqas-Baloch99/AI-Chatbox" style='color: var(--primary-color); text-decoration: none;'><span style='margin-right: 0.5rem;'>🐙</span> GitHub</a></p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    chat_container = st.container()
    with chat_container:
        assistant_idx = 0
        for message in st.session_state.messages:
            if message["role"] == "assistant":
                st.markdown(f"""
                    <div class="assistant-message">
                        <img src="{BOT_AVATAR}" class="assistant-avatar">
                        <div class="message-content">
                            {message["content"]}
                            <div class="response-time">
                                Response time: {st.session_state.response_times[assistant_idx]:.2f}s
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                assistant_idx += 1
            else:
                with st.chat_message("user", avatar="👤"):
                    st.markdown(message["content"])

    if prompt := st.chat_input("Ask anything...", key="chat_input"):
        api_key = get_api_key()
        if not api_key:
            return

        try:
            client = Groq(api_key=api_key)
            st.session_state.messages.append({"role": "user", "content": prompt})

            with st.spinner("AI is thinking..."):
                start_time = time.time()
                response = client.chat.completions.create(
                    model=selected_model,
                    messages=[{"role": m["role"], "content": m["content"]} 
                            for m in st.session_state.messages[-5:]],
                    temperature=0.7,
                    stream=True
                )

                full_response = []
                message_placeholder = st.empty()
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        full_response.append(chunk.choices[0].delta.content)
                        message_placeholder.markdown(f"""
                            <div class="assistant-message">
                                <img src="{BOT_AVATAR}" class="assistant-avatar">
                                <div class="message-content">
                                    {"".join(full_response).strip()}
                                    <div class="response-time">Generating...</div>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)

            response_time = time.time() - start_time
            st.session_state.messages.append({"role": "assistant", "content": "".join(full_response).strip()})
            st.session_state.response_times.append(response_time)
            st.rerun()

        except Exception as e:
            st.error(f"⚠️ Oops! Something went wrong: {str(e)}")
            if st.session_state.messages[-1]["role"] == "user":
                st.session_state.messages.pop()

if __name__ == "__main__":
    main()
