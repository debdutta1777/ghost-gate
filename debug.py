import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ Error: API Key is missing.")
else:
    print(f"✅ Key found: {api_key[:5]}...")
    genai.configure(api_key=api_key)
    
    print("\n🔍 Asking Google what models are available to you...")
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f" - {m.name}")
    except Exception as e:
        print(f"❌ Error connecting: {e}")