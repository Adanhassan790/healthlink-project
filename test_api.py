import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv('OPENAI_API_KEY')
print(f"API Key found: {bool(api_key)}")
print(f"API Key starts with: {api_key[:15] if api_key else 'None'}...")

if api_key:
    try:
        print("Testing OpenAI API connection...")
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say hello"}],
            max_tokens=10
        )
        print(f"✅ API connection successful!")
        print(f"Response: {response.choices[0].message.content}")
    except Exception as e:
        print(f"❌ API Error: {type(e).__name__}: {str(e)}")
else:
    print("❌ API key not found in .env")
