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

user_input = st.text_input("You:", "")

if st.button("Send"):
    if user_input:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "user", "content": user_input}
            ],
            model="gemma2-9b-it"
        )

        bot_response = chat_completion.choices[0].message.content
        st.write("Groq:", bot_response)
    else:
        st.warning("Please enter a message to send.")
