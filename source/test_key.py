import os
from dotenv import load_dotenv
from google import genai
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
client = genai.Client(api_key=os.environ.get("API_KEY"))
response = client.models.generate_content(
    model='gemini-3.5-flash-lite',
    contents='say hello'
)
print(response.text)
