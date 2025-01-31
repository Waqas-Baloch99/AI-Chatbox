import streamlit as st
from groq import Groq
import os
import time
import re  # For input validation

# ======================
#  CONFIGURATION
# ======================
DEVELOPER = "Waqas Baloch"
EMAIL = "waqaskhosa99@gmail.com"
LINKEDIN = "https://www.linkedin.com/in/waqas-baloch"
GITHUB = "https://github.com/Waqas-Baloch99/AI-Chatbox"
BOT_AVATAR = "https://cdn-icons-png.flaticon.com/512/4712/4712035.png"
MODEL_INFO = {
    "mixtral-8x7b-32768": {
        "description": "High-quality text generation with 8 experts mixture",
        "max_tokens": 32768
    },
    "llama-3.3-70b-versatile": {
        "description": "Large 70B parameter model for complex tasks",
        "max_tokens": 4096
    },
    "deepseek-r1-distill-llama-70b": {
        "description": "Distilled version optimized for speed",
        "max_tokens": 4096
    }
}

# ======================
#  CUSTOM CSS
# ======================
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
            max-width: 100%;
            padding: 1.5rem !important;
            font-family: 'Segoe UI', sans-serif;
        }}
        
        .stChatMessage {{
            max-width: 90%;
            margin: 1rem auto !important;
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
        }}
        
        .assistant-avatar {{
            flex-shrink: 0;
            width: 50px;
            height: 50px;
            border-radius: 50%;
            box-shadow: 0 5px 15px rgba(78, 204, 163, 0.3);
        }}
        
        .message-content {{
            flex-grow: 1;
            overflow-x: auto;
        }}
        
        .message-content pre {{
            background: rgba(0, 0, 0, 0.2);
            padding: 1rem;
            border-radius: 8px;
            overflow-x: auto;
        }}
        
        .response-time {{
            font-size: 0.8rem;
            color: var(--primary-color);
            text-align: right;
            margin-top: 0.5rem;
        }}
        
        /* Mobile Optimizations */
        @media (max-width: 768px) {{
            .assistant-avatar {{
                width: 40px;
                height: 40px;
            }}
            
            .stChatInput {{
                bottom: 20px;
                padding: 0 1rem;
            }}
            
            .stChatMessage {{
                max-width: 100%;
                margin: 0.5rem auto !important;
            }}
        }}
        
        /* Typing animation */
        @keyframes typing {{
            from {{ width: 0 }}
            to {{ width: 100% }}
        }}
        
        .typing-indicator {{
            display: inline-block;
            overflow: hidden;
            border-right: 2px solid var(--primary-color);
            white-space: nowrap;
            animation: typing 1s steps(40) infinite;
        }}
        
        .social-badge {{
            transition: transform 0.3s ease;
        }}
        .social-badge:hover {{
            transform: translateY(-2px);
        }}
    </style>
    """, unsafe_allow_html=True)

# ======================
#  ERROR HANDLING
# ======================
def handle_api_error(e):
    error_messages = {
        "404": "🔍 Model not found. Please check the model selection!",
        "401": "🔑 Authentication failed. Verify your API key!",
        "429": "🚦 API rate limit exceeded. Please wait before sending new requests.",
        "500": "🌐 Server error. Please try again later."
    }
    return error_messages.get(str(e.status_code), f"⚠️ Error: {str(e)}")

# ======================
#  SIDEBAR COMPONENT
# ======================
def render_sidebar():
    with st.sidebar:
        st.title("🧑💻 Developer Info")
        st.markdown(f"""
            <div style="text-align:center; margin-bottom:1.5rem;">
                <img src="{BOT_AVATAR}" style="width:100px; border-radius:50%; margin:0 auto;">
                <h3 style="color:#4ecca3; margin:0.5rem 0;">{DEVELOPER}</h3>
                <div style="display:flex; gap:0.5rem; justify-content:center;">
                    <a href="mailto:{EMAIL}" target="_blank" title="Email">
                        <img src="https://img.icons8.com/fluency/48/000000/gmail.png" style="width:32px; height:32px;">
                    </a>
                    <a href="{LINKEDIN}" target="_blank" title="LinkedIn">
                        <img src="https://img.icons8.com/color/48/000000/linkedin.png" style="width:32px; height:32px;">
                    </a>
                    <a href="{GITHUB}" target="_blank" title="GitHub">
                        <img src="https://img.icons8.com/fluency/48/000000/github.png" style="width:32px; height:32px;">
                    </a>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        st.header("⚙️ Settings")
        selected_model = st.selectbox(
            "Select AI Model",
            options=list(MODEL_INFO.keys()),
            format_func=lambda x: f"{x} ({MODEL_INFO[x]['max_tokens']} tokens)",
            help="Select the AI model based on your needs"
        )
        
        with st.expander("Model Details"):
            st.markdown(f"""
                **{selected_model}**  
                {MODEL_INFO[selected_model]['description']}  
                Max tokens: {MODEL_INFO[selected_model]['max_tokens']}
            """)
        
        if st.button("🧹 Clear Chat History", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
        
        st.divider()
        st.caption(f"v1.1.0 | Made with ❤️ by {DEVELOPER}")

        return selected_model

# ======================
#  CHAT MESSAGES DISPLAY
# ======================
def display_messages():
    for message in st.session_state.messages:
        if message["role"] == "assistant":
            with st.chat_message("assistant"):
                st.markdown(f"""
                    <div class="assistant-message">
                        <img src="{BOT_AVATAR}" class="assistant-avatar">
                        <div class="message-content">
                            {message["content"]}
                            {f'<div class="response-time">{message.get("response_time", "")}</div>' 
                             if "response_time" in message else ''}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            with st.chat_message("user", avatar="👤"):
                st.markdown(message["content"])

# ======================
#  MAIN APP FUNCTION
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

    try:
        client = Groq(api_key=st.secrets["GROQ"]["API_KEY"])
    except Exception as e:
        st.error(handle_api_error(e))
        st.stop()

    selected_model = render_sidebar()

    if "messages" not in st.session_state:
        st.session_state.messages = [{
            "role": "assistant",
            "content": "Hello! I'm your AI assistant. How can I help you today? 🌟",
            "response_time": ""
        }]

    display_messages()

    if prompt := st.chat_input("Type your message..."):
        if len(prompt.strip()) < 2:
            st.warning("Please enter a meaningful message (at least 2 characters)")
            return

        st.session_state.messages.append({"role": "user", "content": prompt})
        
        try:
            start_time = time.time()
            with st.spinner("""
                <div class="typing-indicator" style="color: var(--primary-color)">
                    Assistant is typing...
                </div>
            """):
                response = client.chat.completions.create(
                    messages=st.session_state.messages[-5:],
                    model=selected_model,
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
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "".join(full_response).strip(),
                    "response_time": f"Response time: {response_time:.2f}s"
                })
                st.rerun()

        except Exception as e:
            st.error(handle_api_error(e))
            st.session_state.messages.pop()

if __name__ == "__main__":
    main()
