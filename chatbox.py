import os
import streamlit as st
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

api_key = st.secrets["GROQ"]["API_KEY"]

if not api_key:
    raise ValueError("API key not found. Please set the GROQ_API_KEY in the .env file.")

client = Groq(api_key=api_key)

st.title("Groq Chatbot")
st.write("Talk to Groq's model. Enter a message and get a response.")

# Initialize session state for chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Display chat history
for message in st.session_state.chat_history:
    role = "You" if message["role"] == "user" else "Groq"
    st.write(f"{role}: {message['content']}")

user_input = st.text_input("You:", "")

if st.button("Send"):
    if user_input:
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        # Prepare messages for the API call
        messages = [{"role": msg["role"], "content": msg["content"]} for msg in st.session_state.chat_history]

        # Get bot response
        chat_completion = client.chat.completions.create(
            messages=messages,
            model="mixtral-8x7b-32768"  
        )

        bot_response = chat_completion.choices[0].message.content

        # Add bot response to chat history
        st.session_state.chat_history.append({"role": "assistant", "content": bot_response})

        # Display bot response
        st.write("Groq:", bot_response)
    else:
        st.warning("Please enter a message to send.")
