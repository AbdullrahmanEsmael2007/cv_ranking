import streamlit as st
import base64
from openai import OpenAI

client = OpenAI()  # Make sure to set your credentials properly (e.g., environment variables)

st.title("Image Analysis with GPT-4o-mini")

uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
st.image(uploaded_file)
if uploaded_file is not None and st.button("Analyze"):
    file_bytes = uploaded_file.read()
    base64_image = base64.b64encode(file_bytes).decode("utf-8")
    
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Describe the image",
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                ],
            }
        ],
    )
    
    st.write("**AI Response**:")
    st.write(response.choices[0].message.content.strip())
