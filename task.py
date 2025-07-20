import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO

# Load secrets
gemini_api_key = st.secrets["gemini_api_key"]

# Initialize GenAI client with explicit API key
client = genai.Client(api_key=gemini_api_key)

st.title("🖼️ GenAI Image Generator (Gemini Flash)")

# Prompt for user input
prompt = st.text_input("Enter your image prompt:")

if st.button("Generate Image"):
    if not prompt:
        st.error("Please enter a prompt before generating.")
    else:
        with st.spinner("Generating..."):
            try:
                # Request image generation via generate_content
                response = client.models.generate_content(
                    model="gemini-2.0-flash-exp-image-generation",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_modalities=["text", "image"]
                    )
                )

                # Process response
                image_data = None
                for part in response.candidates[0].content.parts:
                    if part.text:
                        st.write(part.text)
                    elif part.inline_data:
                        image_data = part.inline_data.data

                # Display image if present
                if image_data:
                    img = Image.open(BytesIO(image_data))
                    st.image(img, caption="Generated Image", use_column_width=True)
                else:
                    st.error("No image returned by the model.")
            except Exception as e:
                st.error(f"Error generating image: {e}")
