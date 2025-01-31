import streamlit as st
from groq import Groq

# Developer Information
DEVELOPER = "Waqas Baloch"
EMAIL = "waqaskhosa99@gmail.com"
LINKEDIN = "https://www.linkedin.com/in/waqas-baloch"
GITHUB = "https://github.com/Waqas-Baloch99/AI-Chatbox"

# Custom CSS Injection
def inject_custom_css():
    st.markdown(f"""
    <style>
        .main {{
            max-width: 800px;
            padding: 2rem;
        }}
        .developer-info {{
            padding: 1rem;
            background: #f0f2f6;
            border-radius: 10px;
            margin: 1rem 0;
        }}
        .stChatInput {{
            position: fixed;
            bottom: 20px;
            width: 65%;
        }}
        [data-testid="stSidebar"] {{
            width: 300px !important;
        }}
        .error {{
            color: #ff4b4b;
            padding: 1rem;
            border-radius: 0.5rem;
        }}
    </style>
    """, unsafe_allow_html=True)

# Initialize Groq Client with your specified key handling
def initialize_groq_client():
    try:
        api_key = st.secrets["GROQ"]["API_KEY"]
        return Groq(api_key=api_key)
    except KeyError:
        st.error("""
        🔑 API Key Error!
        Please configure your credentials in Streamlit secrets:
        1. Create `.streamlit/secrets.toml`
        2. Add:
           [GROQ]
           API_KEY = "your-api-key-here"
        """)
        st.stop()
    except Exception as e:
        st.error(f"🚨 Initialization Error: {str(e)}")
        st.stop()

# Sidebar with Developer Information
def render_sidebar():
    with st.sidebar:
        st.title("🧑💻 Developer Info")
        st.markdown(f"""
        <div class="developer-info">
            <strong>{DEVELOPER}</strong><br>
            📧 {EMAIL}<br>
            [![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-blue?logo=linkedin)]({LINKEDIN})<br>
            [![GitHub](https://img.shields.io/badge/Source_Code-black?logo=github)]({GITHUB})
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        st.header("⚙️ Settings")
        return st.selectbox(
            "Select AI Model",
            options=["mixtral-8x7b-32768", "llama2-70b-4096"],
            index=0
        )

# Main Chat Interface
def main():
    st.set_page_config(
        page_title="Groq AI Chatbox",
        page_icon="🤖",
        layout="centered"
    )
    inject_custom_css()
    
    st.title("💬 Groq AI Chatbox")
    st.caption("Experience real-time AI conversations powered by Groq's LPU technology")
    
    client = initialize_groq_client()
    selected_model = render_sidebar()
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat messages
    for message in st.session_state.messages:
        avatar = "👤" if message["role"] == "user" else "🤖"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])
    
    # Handle user input
    if prompt := st.chat_input("Type your message..."):
        try:
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user", avatar="👤"):
                st.markdown(prompt)
            
            # Generate response
            with st.spinner("🧠 Processing..."):
                response = client.chat.completions.create(
                    messages=st.session_state.messages[-5:],  # Keep last 5 messages
                    model=selected_model,
                    temperature=0.7
                ).choices[0].message.content
                
                # Add assistant response
                st.session_state.messages.append({"role": "assistant", "content": response})
                with st.chat_message("assistant", avatar="🤖"):
                    st.markdown(response)
                    
        except Exception as e:
            st.error(f"⚠️ Error generating response: {str(e)}")

if __name__ == "__main__":
    main()