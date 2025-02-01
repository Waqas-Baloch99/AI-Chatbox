import streamlit as st
from groq import Groq
import time

# Developer Info
DEVELOPER = "Waqas Baloch"
BOT_AVATAR = "https://cdn-icons-png.flaticon.com/512/4712/4712035.png"

# Available AI Models
MODEL_INFO = {
    "mixtral-8x7b-32768": "High-quality text generation with 8 experts mixture",
    "llama-3.3-70b-versatile": "Large 70B parameter model for complex tasks",
    "deepseek-r1-distill-llama-70b": "Distilled version optimized for speed"
}

# Inject Custom CSS for Styling
def inject_custom_css():
    st.markdown("""
    <style>
        :root {
            --primary-color: #4ecca3;
            --bg-gradient: linear-gradient(135deg, #2a9d8f, #264653);
        }
        
        .main {
            background: var(--bg-gradient) !important;
            color: #e6e6e6;
            padding: 1.5rem !important;
            font-family: 'Segoe UI', sans-serif;
        }
        
        .assistant-message {
            display: flex;
            align-items: flex-start;
            gap: 1.2rem;
            padding: 1rem;
            background: rgba(42, 157, 143, 0.15);
            border-radius: 15px;
            margin: 1rem 0;
            max-width: 85%;
            width: fit-content;
            border: 1px solid rgba(78, 204, 163, 0.2);
        }
        
        .user-message {
            background: rgba(78, 204, 163, 0.25);
            padding: 1rem 1.5rem;
            border-radius: 20px 5px 20px 20px;
            margin: 0.8rem 0 0.8rem auto;
            max-width: 75%;
            width: fit-content;
            word-break: break-word;
            animation: slideIn 0.3s ease-out;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            border: 1px solid rgba(78, 204, 163, 0.4);
            font-size: 0.95rem;
            line-height: 1.4;
        }

        @keyframes slideIn {
            from {
                transform: translateX(20px);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        .assistant-avatar {
            width: 50px;
            height: 50px;
            border-radius: 50%;
            box-shadow: 0 5px 15px rgba(78, 204, 163, 0.3);
        }
        
        .response-time {
            color: #4ecca3 !important;
            font-size: 0.8rem;
            margin-top: 0.5rem;
            font-weight: bold;
            letter-spacing: 0.5px;
        }
        
        .message-content {
            width: calc(100% - 60px);
            padding-right: 10px;
        }
    </style>
    """, unsafe_allow_html=True)

# Main App
def main():
    st.set_page_config(page_title="Groq AI Chatbox", page_icon="🤖")
    inject_custom_css()

    st.title("💬 Groq AI Chatbox")
    st.caption("Real-time AI conversations powered by Groq's LPU technology")

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "response_times" not in st.session_state:
        st.session_state.response_times = []

    # Sidebar Settings
    with st.sidebar:
        st.title("⚙️ Settings")  
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
            <p style='margin-top: 1rem; font-size: 0.9rem;'>waqaskhos99@gmail.com</p>
        </div>
        """, unsafe_allow_html=True)

    # Display chat history
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

    # User Input & AI Response
    if prompt := st.chat_input("Type your message..."):
        try:
            client = Groq(api_key=st.secrets["GROQ"]["API_KEY"])
            
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            start_time = time.time()
            response = client.chat.completions.create(
                model=selected_model,
                messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-4:]],
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
