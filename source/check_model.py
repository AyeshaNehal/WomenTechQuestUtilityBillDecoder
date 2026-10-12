import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
client = genai.Client(api_key=os.environ.get("API_KEY"))

model_name = 'gemini-3.5-flash-lite'
print("Checking model info for:", model_name)
try:
    info = client.models.get(model=model_name)
    print(info)
except Exception as e:
    print("Could not get model info:", e)

print("\nTesting structured output...")
try:
    response = client.models.generate_content(
        model=model_name,
        contents='Give me a JSON object with {"status": "ok"}',
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.0,
        )
    )
    print("Structured output response:", response.text)
except Exception as e:
    print("Structured output error:", e)

print("\nTesting seed support...")
try:
    response = client.models.generate_content(
        model=model_name,
        contents='Give me a random number',
        config=types.GenerateContentConfig(
            seed=42,
        )
    )
    print("Seed supported:", response.text)
except Exception as e:
    print("Seed error:", e)

print("\nTesting thinking config...")
try:
    response = client.models.generate_content(
        model=model_name,
        contents='Hello',
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget_tokens=100)
        )
    )
    print("Thinking supported:", response.text)
except Exception as e:
    print("Thinking error:", e)
