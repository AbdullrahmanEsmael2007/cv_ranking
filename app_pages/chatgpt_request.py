import streamlit as st
from openai import OpenAI

if "key"  in st.session_state:
    client = OpenAI(api_key=st.session_state.key)

def request(prompt, temperature=0.7, max_tokens=1000):
    print("Entered with prompt",prompt)
    # Allow passing either a string (single prompt) or a list of messages (conversation history)
    if isinstance(prompt, str):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    else:
        messages = prompt

    try:
        response = client.chat.completions.create(
            model="gpt-4o",  # or another model of your choice
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return None

print(request("hello"))