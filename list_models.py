from dotenv import load_dotenv
load_dotenv()

from google import genai
client = genai.Client()

print("Available models:")
for m in client.models.list():
    if 'flash' in m.name or 'pro' in m.name:
        print("-", m.name)
