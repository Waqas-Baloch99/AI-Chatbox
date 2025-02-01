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
            --primary-color: #6C63FF;
            --secondary-color: #2F2E41;
            --bg-gradient: linear-gradient(135deg, #0F0C29, #302B63);
        }}
        
        .main {{
            background: var(--bg-gradient);
            color: #ffffff;
            font-family: 'Segoe UI', sans-serif;
            position: relative;
            overflow-x: hidden;
        }}
        
        .assistant-message {{
            background: linear-gradient(145deg, rgba(108, 99, 255, 0.1), rgba(47, 46, 65, 0.2));
            border-radius: 20px 20px 20px 5px;
            padding: 1.2rem;
            margin: 0.8rem 0;
            border: 1px solid rgba(108, 99, 255, 0.2);
            animation: slideIn 0.3s ease-out;
            display: flex;
            align-items: center;
            gap: 1rem;
            max-width: 75%;
            animation: fadeIn 0.5s ease-out;

        }}
        
       
        
        .assistant-avatar {{
            width: 45px;
            height: 45px;
            border-radius: 50%;
            box-shadow: 0 8px 20px rgba(108, 99, 255, 0.3);
            animation: float 3s ease-in-out infinite bounceIn 0.6s ease-out;
            flex-shrink: 0;
        }}
        
        .message-content {{
            flex-grow: 1;
            padding: 0 1rem;
            font-size: 0.95rem;
            line-height: 1.4;
        }}
        
        .response-time {{
            font-size: 0.75rem;
            color: var(--primary-color);
            text-align: right;
            margin-top: 0.5rem;
            opacity: 0.8;
        }}
        
        /* Keep other existing styles (boat animation, sidebar, etc) */
    </style>
    <div class="boat">⛵</div>
    """, unsafe_allow_html=True)

def create_sidebar():
    with st.sidebar:
        st.title("⚙️ Settings")
        selected_model = st.selectbox(
            "AI Model", list(MODEL_INFO.keys()),
            format_func=lambda x: f"{x.split('-')[0].title()} ({'32768' if 'mixtral' in x else '4096'} tokens)",
            help="Select an AI model: " + "; ".join([f"{k}: {v}" for k, v in MODEL_INFO.items()])
        )
        if st.button("🧹 Clear Chat History", use_container_width=True, type="secondary"):
            st.session_state.clear()
            st.rerun()
        st.divider()
        st.markdown(f"""
        <div style='text-align:center;padding:1.5rem 0;'>
            <h4 style='color:var(--primary-color);margin-bottom:1.5rem;'>Developed by {DEVELOPER}</h4>
            <div style='display:grid;gap:1rem;'>
                <a href="mailto:waqaskhos99@gmail.com" style='text-decoration:none;'>
                    <button style='width:100%;background:rgba(108,99,255,0.1);border:1px solid var(--primary-color);border-radius:8px;padding:0.7rem;color:#fff;display:flex;align-items:center;justify-content:center;gap:0.8rem;'>
                        <img src="https://cdn-icons-png.flaticon.com/512/281/281769.png" style="width:24px;height:24px;"> Email
                    </button>
                </a>
                <a href="https://www.linkedin.com/in/waqas-baloch" target="_blank" style='text-decoration:none;'>
                    <button style='width:100%;background:rgba(108,99,255,0.1);border:1px solid var(--primary-color);border-radius:8px;padding:0.7rem;color:#fff;display:flex;align-items:center;justify-content:center;gap:0.8rem;'>
                        <img src="https://cdn-icons-png.flaticon.com/512/174/174857.png" style="width:24px;height:24px;"> LinkedIn
                    </button>
                </a>
                <a href="https://github.com/Waqas-Baloch99/AI-Chatbox" target="_blank" style='text-decoration:none;'>
                    <button style='width:100%;background:rgba(108,99,255,0.1);border:1px solid var(--primary-color);border-radius:8px;padding:0.7rem;color:#fff;display:flex;align-items:center;justify-content:center;gap:0.8rem;'>
                        <img src="https://cdn-icons-png.flaticon.com/512/25/25231.png" style="width:24px;height:24px;"> GitHub
                    </button>
                </a>
            </div>
        </div>""", unsafe_allow_html=True)
        st.session_state.selected_model = selected_model

def display_chat_messages():
    for idx, message in enumerate(st.session_state.get("messages", [])):
        if message["role"] == "assistant":
            with st.chat_message("assistant"):
                st.markdown(f"""
                    <div class="assistant-message">
                        <img src="{BOT_AVATAR}" class="assistant-avatar">
                        <div class="message-content">
                            {message["content"]}
                            {f'<div class="response-time">Response time: {st.session_state.response_times[idx//2]:.2f}s</div>' 
                             if idx//2 < len(st.session_state.response_times) else ''}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            with st.chat_message("user", avatar="👤"):
                st.markdown(f"""
                    <div class="user-message" id="message-{idx}">
                        {message["content"]}
                    </div>
                """, unsafe_allow_html=True)
                
                if idx == len(st.session_state.messages)-1:
                    st.markdown(f"""
                    <script>
                        document.getElementById('message-{idx}').scrollIntoView({{behavior: 'smooth'}});
                    </script>
                    """, unsafe_allow_html=True)

def handle_chat_input():
    if prompt := st.chat_input("Type your message..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        try:
            client = Groq(api_key=st.secrets.GROQ.API_KEY)
            start_time = time.time()
            response = client.chat.completions.create(
                model=st.session_state.selected_model,
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

            st.session_state.messages.append({"role": "assistant", "content": "".join(full_response).strip()})
            st.session_state.response_times = st.session_state.get("response_times", []) + [time.time() - start_time]
            st.rerun()

        except Exception as e:
            st.error(f"⚠️ Error: {str(e)}")
            st.session_state.messages.pop()

def main():
    st.set_page_config(page_title="Groq AI Chatbox", page_icon="🤖", layout="wide")
    inject_custom_css()
    st.title("💬 Groq AI Chatbox")
    st.caption("Real-time AI conversations powered by Groq's LPU Technology 🌊")

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "response_times" not in st.session_state:
        st.session_state.response_times = []

    create_sidebar()
    display_chat_messages()
    handle_chat_input()

if __name__ == "__main__":
    main()
