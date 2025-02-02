import streamlit as st
from groq import Groq
import time
from PIL import Image
import io
import base64

DEVELOPER = "Waqas Baloch"
BOT_AVATAR = "https://cdn-icons-png.flaticon.com/512/4712/4712035.png"
MODEL_INFO = {
    "mixtral-8x7b-32768": "Mixtral 8x7B (32k context)",
    "llama-3.3-70b-versatile": "Llama 70B (4k context)",
    "deepseek-r1-distill-llama-70b": "Deepseek 70B (4k context)"
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
            position: relative; 
            animation: fadeIn 0.5s ease-out; 
        }}
        .assistant-avatar {{ 
            width: 50px; 
            height: 50px; 
            border-radius: 50%; 
            box-shadow: 0 5px 15px rgba(78, 204, 163, 0.3); 
            animation: float 3s ease-in-out infinite, bounceIn 0.6s ease-out; 
        }}
        .message-content {{ 
            flex-grow: 1; 
            overflow-x: auto;
        }}
        .response-time {{ 
            font-size: 0.8rem; 
            color: var(--primary-color); 
            text-align: right; 
            margin-top: 0.5rem; 
        }}
        .image-message {{
            max-width: 100%;
            border-radius: 10px;
            margin-top: 0.5rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        .upload-column {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
            padding-bottom: 1rem;
        }}
        @media (max-width: 768px) {{ 
            .main {{ 
                padding: 1rem !important; 
                min-width: unset !important;
            }}
            .assistant-message {{
                flex-direction: column;
                gap: 0.8rem;
                padding: 0.8rem;
            }}
            .assistant-avatar {{
                width: 40px; 
                height: 40px;
            }}
            .stChatInput {{ 
                bottom: 20px; 
                padding: 0 1rem; 
                position: fixed !important;
                background: var(--bg-gradient);
                z-index: 100;
            }}
            .stChatInput textarea {{
                min-height: 40px !important;
                font-size: 0.9rem !important;
            }}
            .sidebar .sidebar-content {{
                width: 200px !important;
            }}
            .message-content {{
                font-size: 0.95rem;
            }}
            .response-time {{
                font-size: 0.7rem;
            }}
            .image-message {{
                max-width: 90%;
            }}
            .upload-column {{
                flex-direction: column;
            }}
        }}
        @media (max-width: 480px) {{
            .assistant-avatar {{
                width: 35px; 
                height: 35px;
            }}
            .stChatInput {{
                bottom: 10px;
                padding: 0 0.5rem;
            }}
            .stChatInput textarea {{
                font-size: 0.85rem !important;
            }}
            .stMarkdown h1 {{
                font-size: 1.5rem !important;
            }}
        }}
        @keyframes fadeIn {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
        @keyframes bounceIn {{ 
            0% {{ transform: scale(0.5); opacity: 0; }} 
            50% {{ transform: scale(1.05); opacity: 0.7; }} 
            70% {{ transform: scale(0.95); opacity: 0.9; }} 
            100% {{ transform: scale(1); opacity: 1; }} 
        }}
        @keyframes float {{ 
            0%, 100% {{ transform: translateY(0px); }} 
            50% {{ transform: translateY(-20px); }} 
        }}
    </style>
    """, unsafe_allow_html=True)

def main():
    st.set_page_config(page_title="AI Chatbox", page_icon="🤖", layout="centered")
    inject_custom_css()

    st.title("💬 AI Chatbox")
    st.caption("Real-time AI conversations powered by Groq's LPU technology")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    with st.sidebar:
        st.title("⚙️ Settings")
        selected_model = st.selectbox("AI Model", list(MODEL_INFO.keys()), format_func=lambda x: MODEL_INFO[x])

        if st.button("🧹 Clear Chat History", use_container_width=True):
            st.session_state.messages = []
            st.experimental_rerun()

        st.divider()

        st.markdown(f"""
        <div style='text-align:center; color:#4ecca3; padding: 1rem 0; border-top: 1px solid #4ecca3; border-bottom: 1px solid #4ecca3;'>  
            <div style="font-weight: bold; margin-bottom: 0.5rem;">Developed by {DEVELOPER}</div>
            <div style="display: flex; justify-content: center; gap: 1rem; flex-wrap: wrap;">
                <a href="mailto:waqaskhos99@gmail.com" target="_blank" style="display: flex; align-items: center; text-decoration: none; color: inherit;">
                    <img src="https://img.icons8.com/color/48/000000/new-post.png" alt="Email" style="width: 24px; height: 24px; margin-right: 0.5rem;"/>
                    <span style="font-size: 0.9rem;">Email</span>
                </a>
                <a href="https://www.linkedin.com/in/waqas-baloch" target="_blank" style="display: flex; align-items: center; text-decoration: none; color: inherit;">
                    <img src="https://img.icons8.com/color/48/000000/linkedin.png" alt="LinkedIn" style="width: 24px; height: 24px; margin-right: 0.5rem;"/>
                    <span style="font-size: 0.9rem;">LinkedIn</span>
                </a>
                <a href="https://github.com/Waqas-Baloch99/AI-Chatbox" target="_blank" style="display: flex; align-items: center; text-decoration: none; color: inherit;">
                    <img src="https://img.icons8.com/ios-filled/50/000000/github.png" alt="GitHub" style="width: 24px; height: 24px; margin-right: 0.5rem;"/>
                    <span style="font-size: 0.9rem;">GitHub</span>
                </a>
            </div>
        </div>
        """, unsafe_allow_html=True)

    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar="👤" if message["role"] == "user" else BOT_AVATAR):
            if message["type"] == "text":
                st.markdown(message["content"])
            elif message["type"] == "image":
                st.image(Image.open(io.BytesIO(message["content"])), caption="Uploaded Image", use_column_width=True)
            
            if "response_time" in message and message["role"] == "assistant":
                st.markdown(f'<div class="response-time">Response time: {message["response_time"]:.2f}s</div>', unsafe_allow_html=True)

    # Image upload and chat input
    upload_col, chat_col = st.columns([1, 4])
    with upload_col:
        uploaded_file = st.file_uploader(
            "📷", 
            type=["jpg", "jpeg", "png"], 
            accept_multiple_files=False,
            key="file_uploader",
            help="Upload an image",
            label_visibility="collapsed"
        )
    with chat_col:
        prompt = st.chat_input("Type your message...")

    if uploaded_file:
        image = Image.open(uploaded_file)
        img_bytes = io.BytesIO()
        image.save(img_bytes, format="PNG")
        st.session_state.messages.append({
            "role": "user",
            "type": "image",
            "content": img_bytes.getvalue(),
            "timestamp": time.time()
        })
        uploaded_file = None
        st.experimental_rerun()

    if prompt:
        try:
            client = Groq(api_key=st.secrets.GROQ.API_KEY)
            st.session_state.messages.append({
                "role": "user",
                "type": "text",
                "content": prompt,
                "timestamp": time.time()
            })

            start_time = time.time()
            text_messages = [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages[-4:]
                if m["type"] == "text"
            ]

            response = client.chat.completions.create(
                model=selected_model,
                messages=text_messages,
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
            full_response_text = "".join(full_response).strip()
            st.session_state.messages.append({
                "role": "assistant",
                "type": "text",
                "content": full_response_text,
                "response_time": response_time
            })
            st.experimental_rerun()

        except Exception as e:
            st.error(f"⚠️ Error: {str(e)}")
            if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
                st.session_state.messages.pop()

if __name__ == "__main__":
    main()
