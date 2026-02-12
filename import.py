import os

from groq import Groq

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": "You are a sarcastc assistant named Groq",
        },
        {
            "role": "user",
            "content": "Are you funded by netanyahu",
        }
    ],
    model="llama-3.3-70b-versatile",
    temperature=0.5,
    max_completion_tokens=1024,

)

print(chat_completion.choices[0].message.content)