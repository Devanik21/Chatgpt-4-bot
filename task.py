import streamlit as st
from io import BytesIO
from PIL import Image
import torch
from diffusers import StableDiffusionPipeline

# Load database secrets (optional)
db_username = st.secrets["db_username"]
db_password = st.secrets["db_password"]
# Use db_username/db_password for DB connections here

# Sidebar settings
st.sidebar.title("Settings")
model_id = st.sidebar.selectbox(
    "Choose a model:",
    [
        "stabilityai/stable-diffusion-2-1",
        "prompthero/openjourney",
        "dreamlike-art/dreamshaper-v7",
    ],
)
num_images = st.sidebar.slider("Number of images", 1, 4, 1)

# Cache the pipeline loading
@st.cache_resource
def load_pipeline(model_name):
    return StableDiffusionPipeline.from_pretrained(
        model_name, torch_dtype=torch.float16
    ).to("cuda" if torch.cuda.is_available() else "cpu")

pipe = load_pipeline(model_id)

# App UI
st.title("🖼️ Local Stable Diffusion Generator")
prompt = st.text_input("Enter your prompt:", "A futuristic cityscape at sunset")

if st.button("Generate Images"):
    with st.spinner("Generating..."):
        images = pipe(
            prompt=prompt,
            num_inference_steps=30,
            guidance_scale=7.5,
            num_images_per_prompt=num_images,
        ).images
        for i, img in enumerate(images, 1):
            st.image(img, caption=f"{model_id} #{i}", use_column_width=True)
