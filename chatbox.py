import streamlit as st
import requests
import pytesseract
from PIL import Image
import io
import os
import groq  # Ensure you have installed groq (`pip install groq`)

# Load API key from Streamlit secrets
API_KEY = st.secrets["GROQ"]["API_KEY"]  # Ensure API key is set in secrets
BOT_AVATAR = "https://cdn-icons-png.flaticon.com/512/4712/4712035.png"  # Avatar URL

# Initialize Groq client
client = groq.Client(api_key=API_KEY)

# Streamlit UI Setup
st.set_page_config(page_title="AI Chatbot with OCR", page_icon="🤖", layout="wide")
st.title("🤖 AI Chatbot with OCR")

# Model options for selection
MODEL_OPTIONS = ["llama3-8b-8192", "gpt-4", "gpt-3.5-turbo"]
selected_model = st.selectbox("Select AI Model", MODEL_OPTIONS)

# Developer Mode Option (Show extra details like errors)
developer_mode = st.checkbox("Enable Developer Mode (Show Errors)")

# File Uploader for OCR (will be inside a text area-like space)
uploaded_file = st.file_uploader("Upload an image (JPG/PNG) for OCR", type=["png", "jpg", "jpeg"])

# Extract text from image
def extract_text_from_image(image_file):
    try:
        image = Image.open(image_file)
        text = pytesseract.image_to_string(image)
        return text.strip()
    except Exception as e:
        return f"Error processing image: {str(e)}"

# Chat Interface
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for msg in st.session_state.messages:
    st.markdown(
        f"""
        <div class="{'user-message' if msg['role'] == 'user' else 'assistant-message'}">
            <img src="{msg['avatar']}" class="{'user-avatar' if msg['role'] == 'user' else 'assistant-avatar'}">
            <div class="message-content">{msg['content']}</div>
        </div>
        """, unsafe_allow_html=True
    )

# Get user input (Text Area for messages and OCR-related text)
user_input = st.text_area("Enter your message:", height=100)

# Add an Image Upload button in the text bar area
if uploaded_file:
    extracted_text = extract_text_from_image(uploaded_file)
    st.text_area("Extracted Text:", extracted_text, height=150)
    
    # Option to send extracted text to AI model for processing
    if st.button("Analyze Extracted Text with AI"):
        with st.spinner("Analyzing text..."):
            try:
                response = client.chat.completions.create(
                    model=selected_model,  # Model selection dynamically
                    messages=[{"role": "user", "content": extracted_text}],
                    stream=True,
                )
                
                full_response = []
                message_placeholder = st.empty()
                
                for chunk in response:
                    if hasattr(chunk.choices[0].delta, "content") and chunk.choices[0].delta.content:
                        full_response.append(chunk.choices[0].delta.content)
                        message_placeholder.markdown(
                            f"""
                            <div class="assistant-message">
                                <img src="{BOT_AVATAR}" class="assistant-avatar">
                                <div class="message-content">{"".join(full_response).strip()}</div>
                            </div>
                            """, unsafe_allow_html=True
                        )
                
                assistant_reply = "".join(full_response).strip()
                st.session_state.messages.append({"role": "assistant", "content": assistant_reply, "avatar": BOT_AVATAR})

            except Exception as e:
                if developer_mode:
                    st.error(f"API Error: {str(e)}")
                else:
                    st.error("Something went wrong. Please try again.")

# Get the user message and send it to the selected model
if user_input:
    # Display user message
    st.session_state.messages.append({"role": "user", "content": user_input, "avatar": "https://cdn-icons-png.flaticon.com/512/4712/4712105.png"})
    
    # Groq API Call
    with st.spinner("Thinking..."):
        try:
            response = client.chat.completions.create(
                model=selected_model,  # Model selection dynamically
                messages=[{"role": "user", "content": user_input}],
                stream=True,
            )
            
            full_response = []
            message_placeholder = st.empty()
            
            # Stream AI response
            for chunk in response:
                if hasattr(chunk.choices[0].delta, "content") and chunk.choices[0].delta.content:
                    full_response.append(chunk.choices[0].delta.content)
                    message_placeholder.markdown(
                        f"""
                        <div class="assistant-message">
                            <img src="{BOT_AVATAR}" class="assistant-avatar">
                            <div class="message-content">{"".join(full_response).strip()}</div>
                        </div>
                        """, unsafe_allow_html=True
                    )
            
            assistant_reply = "".join(full_response).strip()
            st.session_state.messages.append({"role": "assistant", "content": assistant_reply, "avatar": BOT_AVATAR})

        except Exception as e:
            if developer_mode:
                st.error(f"API Error: {str(e)}")
            else:
                st.error("Something went wrong. Please try again.")

# CSS Styling for Chat Interface
st.markdown(
    """
    <style>
    .user-message, .assistant-message {
        display: flex;
        align-items: center;
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
    }
    .user-avatar, .assistant-avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        margin-right: 10px;
    }
    .message-content {
        background-color: #f3f3f3;
        padding: 10px;
        border-radius: 10px;
    }
    .user-message {
        justify-content: flex-end;
    }
    .assistant-message {
        justify-content: flex-start;
        background-color: #e0f2f1;
    }
    </style>
    """, unsafe_allow_html=True
)

