import streamlit as st
from groq import Groq
import time
from PIL import Image
import pytesseract  # Requires Tesseract OCR installed

DEVELOPER = "Waqas Baloch"
BOT_AVATAR = "https://cdn-icons-png.flaticon.com/512/4712/4712035.png"

# Ensure Tesseract path is set correctly (modify based on your system)
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

def process_image(uploaded_file):
    try:
        image = Image.open(uploaded_file)
        text = pytesseract.image_to_string(image)
        return text.strip(), image
    except Exception as e:
        st.error(f"⚠️ Error processing image: {str(e)}")
        return None, None

def main():
    st.set_page_config(page_title="AI Chatbox", page_icon="🤖")
    st.title("💬 AI Chatbox")
    st.caption("Real-time AI conversations powered by Groq")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Image upload
    uploaded_file = st.file_uploader("📷 Upload an image", type=["png", "jpg", "jpeg"])
    if uploaded_file is not None:
        ocr_text, processed_image = process_image(uploaded_file)
        if ocr_text:
            st.image(processed_image, caption="Uploaded Image", use_column_width=True)
            st.success("✅ Text extracted successfully!")
            st.write(ocr_text)

    # Chat input
    prompt = st.chat_input("Type your message...")
    if prompt:
        try:
            client = Groq(api_key=st.secrets.GROQ.API_KEY)
            st.session_state.messages.append({"role": "user", "content": prompt})
            response = client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            full_response = response.choices[0].text.strip()
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            st.write(full_response)

        except Exception as e:
            st.error(f"⚠️ Error: {str(e)}")

if __name__ == "__main__":
    main()
