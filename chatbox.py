import streamlit as st
from transformers import GPT2LMHeadModel, GPT2Tokenizer

# Initialize the GPT-2 model and tokenizer
model = GPT2LMHeadModel.from_pretrained('gpt2')
tokenizer = GPT2Tokenizer.from_pretrained('gpt2')

# Set pad_token_id to eos_token_id (end-of-sequence token)
tokenizer.pad_token = tokenizer.eos_token  # Assign eos_token as the pad_token
model.config.pad_token_id = model.config.eos_token_id

# Streamlit UI components
st.title("GPT-2 Text Generator")
st.write("Enter a prompt below, and GPT-2 will generate a continuation for you:")

# Text input box
input_text = st.text_area("Enter your text here:")

# Button to generate text
if st.button("Generate"):
    if input_text:
        with st.spinner('Generating text...'):
            try:
                # Encode the input text and include attention_mask
                inputs = tokenizer.encode(input_text, return_tensors='pt', padding=True, truncation=True)

                # Generate text based on the input
                output = model.generate(inputs, max_length=150, num_return_sequences=1, no_repeat_ngram_size=2)

                # Decode the generated output into human-readable text
                generated_text = tokenizer.decode(output[0], skip_special_tokens=True)

                # Display the generated text
                st.subheader("Generated Text:")
                st.write(generated_text)
            except Exception as e:
                st.error(f"Error during text generation: {str(e)}")
    else:
        st.write("Please enter some text to get started.")
