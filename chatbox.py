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
            border-radius: 20px;
            padding: 1.5rem;
            margin: 1rem 0;
            border: 1px solid rgba(108, 99, 255, 0.2);
            animation: slideIn 0.3s ease-out;
            display: flex;
            align-items: center;
            gap: 1rem;
        }}
        
        .user-message {{
            background: linear-gradient(145deg, rgba(108, 99, 255, 0.05), rgba(47, 46, 65, 0.1));
            border-radius: 20px;
            padding: 1.5rem;
            margin: 1rem 0;
            border: 1px solid rgba(108, 99, 255, 0.1);
            animation: slideIn 0.3s ease-out;
            text-align: right;
        }}
        
        .assistant-avatar {{
            width: 50px;
            height: 50px;
            border-radius: 50%;
            box-shadow: 0 8px 20px rgba(108, 99, 255, 0.3);
            animation: float 3s ease-in-out infinite;
            flex-shrink: 0;
        }}
        
        .message-content {{
            flex-grow: 1;
            padding-right: 1rem;
        }}
        
        .boat {{
            position: fixed;
            bottom: -50px;
            right: -50px;
            font-size: 80px;
            opacity: 0.1;
            animation: sail 20s linear infinite;
            pointer-events: none;
        }}
        
        @keyframes float {{ 0%,100% {{ transform:translateY(0) }} 50% {{ transform:translateY(-15px) }} }}
        @keyframes sail {{ 0% {{ transform:translateX(100vw) rotate(30deg) }} 100% {{ transform:translateX(-100vw) rotate(30deg) }} }}
        @keyframes slideIn {{ from {{ transform:translateY(20px);opacity:0 }} to {{ transform:translateY(0);opacity:1 }} }}
        
        @media (max-width:768px) {{ 
            .user-message {{ margin-left:10% }} 
            .assistant-avatar {{ width:40px;height:40px }}
        }}
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
                    <button style='width:100%;background:rgba(108,99,255,0.1);border:1px solid var(--primary-color);border-radius:8px;padding:0.5rem;color:#fff;display:flex;align-items:center;justify-content:center;gap:0.5rem;'>✉️ Contact via Email</button>
                </a>
                <a href="https://www.linkedin.com/in/waqas-baloch" target="_blank" style='text-decoration:none;'>
                    <button style='width:100%;background:rgba(108,99,255,0.1);border:1px solid var(--primary-color);border-radius:8px;padding:0.5rem;color:#fff;display:flex;align-items:center;justify-content:center;gap:0.5rem;'>🔗 LinkedIn Profile</button>
                </a>
                <a href="https://github.com/Waqas-Baloch99/AI-Chatbox" target="_blank" style='text-decoration:none;'>
                    <button style='width:100%;background:rgba(108,99,255,0.1);border:1px solid var(--primary-color);border-radius:8px;padding:0.5rem;color:#fff;display:flex;align-items:center;justify-content:center;gap:0.5rem;'>🐙 GitHub Repository</button>
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
                        document.getElementById('message-{idx}').scrollIntoView();
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
