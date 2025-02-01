import streamlit as st
from groq import Groq
import time

DEVELOPER = "Waqas Baloch"
BOT_AVATAR = "https://cdn-icons-png.flaticon.com/512/4712/4712035.png"
MODEL_INFO = {
    "mixtral-8x7b-32768": "High-quality text generation with 8 experts mixture",
    "llama-3.3-70b-versatile": "Large 70B parameter model for complex tasks",
    "deepseek-r1-distill-llama-70b": "Distilled version optimized for speed"
}

def inject_custom_css():
    st.markdown(f"""
    <style>
        :root {{
            --primary-color: #4ecca3;
            --bg-gradient: linear-gradient(135deg, #1a1a2e, #16213e);
        }}
        
        .main {{
            background: var(--bg-gradient); 
            color: #e6e6e6;
            padding: 1.5rem !important;
            font-family: 'Segoe UI', sans-serif;
        }}
        
        .assistant-message {{
            display: flex;
            align-items: flex-start;
            gap: 1.2rem;
            padding: 1rem;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
            margin: 1rem 0;
            max-width: 80%;
            width: fit-content;
        }}
        
        .user-message {{
            display: flex;
            align-items: flex-start;
            gap: 1.2rem;
            padding: 1rem;
            border-radius: 15px;
            margin: 1rem 0;
            max-width: 80%;
            width: fit-content;
        }}
        
        .assistant-avatar {{
            width: 50px;
            height: 50px;
            border-radius: 50%;
            box-shadow: 0 5px 15px rgba(78, 204, 163, 0.3);
            animation: float 3s ease-in-out infinite;
        }}
        
        .response-time {{
            font-size: 0.8rem;
            color: var(--primary-color);
            text-align: right;
            margin-top: 0.5rem;
        }}
        
        .developer-section {{
            text-align: center;
            margin-top: 2rem;
            padding: 1rem;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
        }}
        
        .social-icon {{
            width: 32px;
            height: 32px;
            margin: 0 0.5rem;
            transition: transform 0.3s ease;
        }}
        
        .social-icon:hover {{
            transform: translateY(-3px);
        }}
        
        @keyframes float {{
            0%, 100% {{ transform: translateY(0px); }}
            50% {{ transform: translateY(-15px); }}
        }}
        
        @media (max-width: 768px) {{
            .assistant-avatar {{ width: 40px; height: 40px; }}
            .stChatInput {{ bottom: 20px; padding: 0 1rem; }}
        }}
    </style>
    """, unsafe_allow_html=True)

def main():
    st.set_page_config(page_title="Groq AI Chatbox", page_icon="🤖")
    inject_custom_css()

    st.title("💬 Groq AI Chatbox")
    st.caption("Real-time AI conversations powered by Groq's LPU technology")

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "response_times" not in st.session_state:
        st.session_state.response_times = []

    with st.sidebar:
        st.title("⚙️ Settings")  # Fixed syntax error
        selected_model = st.selectbox("AI Model", list(MODEL_INFO.keys()), 
                                    format_func=lambda x: f"{x} ({'32768' if 'mixtral' in x else '4096'} tokens)")
        
        if st.button("🧹 Clear Chat History", use_container_width=True):
            st.session_state.messages = []
            st.session_state.response_times = []
            st.rerun()

        st.divider()
        st.markdown(f"""
        <div class="developer-section">
            <h4 style='color: var(--primary-color);'>Developed by {DEVELOPER}</h4>
            <div style='margin-top: 1.5rem;'>
                <a href="mailto:waqaskhos99@gmail.com">
                    <img src="https://img.icons8.com/color/48/000000/gmail.png" class="social-icon" alt="Email">
                </a>
                <a href="https://www.linkedin.com/in/waqas-baloch" target="_blank">
                    <img src="https://img.icons8.com/color/48/000000/linkedin.png" class="social-icon" alt="LinkedIn">
                </a>
                <a href="https://github.com/Waqas-Baloch99/AI-Chatbox" target="_blank">
                    <img src="https://img.icons8.com/color/48/000000/github.png" class="social-icon" alt="GitHub">
                </a>
            </div>
            <p style='margin-top: 1rem; font-size: 0.9rem;'>
                waqaskhos99@gmail.com
            </p>
        </div>
        """, unsafe_allow_html=True)

    assistant_idx = 0
    for message in st.session_state.messages:
        if message["role"] == "assistant":
            with st.chat_message("assistant"):
                st.markdown(f"""
                    <div class="assistant-message">
                        <img src="{BOT_AVATAR}" class="assistant-avatar">
                        <div class="message-content">
                            {message["content"]}
                            {f'<div class="response-time">Response time: {st.session_state.response_times[assistant_idx]:.2f}s</div>' 
                             if assistant_idx < len(st.session_state.response_times) else ''}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                assistant_idx += 1
        else:
            with st.chat_message("user", avatar="👤"):
                st.markdown(f"<div class='user-message'>{message['content']}</div>", unsafe_allow_html=True)

    if prompt := st.chat_input("Type your message..."):
        try:
            client = Groq(api_key=st.secrets.GROQ.API_KEY)
            
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            start_time = time.time()
            response = client.chat.completions.create(
                model=selected_model,
                messages=[{"role": m["role"], "content": m["content"]} 
                         for m in st.session_state.messages[-4:]],
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
            st.error(f"⚠️ Error: {str(e)}")
            if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
                st.session_state.messages.pop()

if __name__ == "__main__":
    main()
