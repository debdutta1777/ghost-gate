import os
import google.generativeai as genai
from dotenv import load_dotenv

# 1. Load Environment Variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

print("-" * 40)
print("🔍 GHOST-GATE DIAGNOSTIC TOOL")
print("-" * 40)

# 2. Check API Key
if not api_key:
    print("❌ ERROR: GEMINI_API_KEY is missing from .env file!")
    print("👉 Please check your .env file format.")
    exit()

print(f"✅ API Key found: {api_key[:5]}...{api_key[-4:]}")

# 3. Configure Google AI
try:
    genai.configure(api_key=api_key)
    print("✅ Library configured.")
except Exception as e:
    print(f"❌ Configuration failed: {e}")
    exit()

# 4. List Available Models
print("\n📡 Connecting to Google servers to list models...")
try:
    models = list(genai.list_models())
    available_names = [m.name for m in models if 'generateContent' in m.supported_generation_methods]
    
    if not available_names:
        print("❌ No models found! Your API Key might have zero quota or be restricted.")
    else:
        print(f"✅ Found {len(available_names)} available models:")
        for name in available_names:
            print(f"   - {name}")
            
    # 5. Test Generation
    if available_names:
        target_model = "models/gemini-1.5-flash" if "models/gemini-1.5-flash" in available_names else available_names[0]
        print(f"\n🧪 Testing generation with: {target_model}...")
        model = genai.GenerativeModel(target_model)
        response = model.generate_content("Hello, are you working?")
        print(f"🎉 SUCCESS! Response: {response.text}")
        
except Exception as e:
    print(f"\n❌ FATAL CONNECTION ERROR:\n{e}")
    print("-" * 40)
    print("TROUBLESHOOTING:")
    if "403" in str(e):
        print("👉 API Key is invalid or has API Service disabled in Google Cloud Console.")
    elif "400" in str(e):
        print("👉 API Key might be empty or malformed.")
    elif "429" in str(e):
        print("👉 You have exceeded your free quota. Wait a few minutes.")
    else:
        print("👉 Check your internet connection or firewall.")