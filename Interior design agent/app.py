import streamlit as st
import asyncio
from lib.agent import run_agent
import tempfile
from dotenv import load_dotenv

load_dotenv()
st.title("Interior Designer Agent")
style = st.text_input("Describe your intended interior design styling:")
image_file = st.file_uploader("Upload an image (png or jpg)", type=["png","jpg","jpeg"])

if st.button("Run Agent"):
    if style and image_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
            tmp_file.write(image_file.read())
            tmp_file_path = tmp_file.name

            st.image(image_file,caption="Uploaded Floorplan",use_container_width=True)
            st.write("Running agent...")

            result = asyncio.run(run_agent(style,tmp_file_path))
            if result:
                st.markdown(f"**Response:** {result['text']}")
                if 'image_paths' in result:
                    for img_path in result['image_paths']:
                        st.image(img_path,caption=img_path, use_container_width=True)
            else:
                st.error("No result returned from agent.")
    else:
        st.error("Please provide both a style description and an image")