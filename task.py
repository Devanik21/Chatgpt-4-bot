import streamlit as st
from io import BytesIO
from PIL import Image
from google import genai

# Load secrets
db_username = st.secrets["db_username"]
db_password = st.secrets["db_password"]
gemini_api_key = st.secrets["gemini_api_key"]

# Optionally, connect to your database using db_username and db_password here
# e.g., connection = YourDBClient(username=db_username, password=db_password)

# Initialize GenAI client with secrets
client = genai.Client(api_key=gemini_api_key)

# Streamlit UI
st.title("🖼️ GenAI Image Generator with Secrets")

prompt = st.text_input("Enter your image prompt:", "A futuristic cityscape at sunset")
num_images = st.slider("Number of images", min_value=1, max_value=4, value=1)
aspect = st.selectbox("Aspect ratio", ["1:1", "3:4", "4:3", "9:16", "16:9"])

if st.button("Generate Images"):
    with st.spinner("Generating..."):
        try:
            result = client.models.generate_images(
                model="imagen-3.0-generate-002",
                prompt=prompt,
                config={
                    "number_of_images": num_images,
                    "output_mime_type": "image/jpeg",
                    "person_generation": "ALLOW_ADULT",
                    "aspect_ratio": aspect
                }
            )
            # Display images
            for idx, gen_img in enumerate(result.generated_images, start=1):
                img = Image.open(BytesIO(gen_img.image.image_bytes))
                st.image(img, caption=f"Generated #{idx}", use_column_width=True)
        except Exception as e:
            st.error(f"Error generating images: {e}")
