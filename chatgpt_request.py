import openai
from key import OPENAI_API_KEY
from openai import OpenAI 
client = OpenAI(api_key=OPENAI_API_KEY)

def request(prompt, temperature=0.7, max_tokens=1000):
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
