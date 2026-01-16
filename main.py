import os
import google.generativeai as genai
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from engine import protect_prompt, restore_response, process_pdf_with_secrets, process_image
import uvicorn

# 1. Load the Secret Key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ ERROR: No API Key found in .env file!")
else:
    genai.configure(api_key=api_key)
    print("✅ Gemini AI Connected")

app = FastAPI(title="Ghost-Gate")

# Mount the static files (CSS/JS/HTML)
app.mount("/static", StaticFiles(directory="static"), name="static")

class ChatRequest(BaseModel):
    prompt: str
    custom_secrets: list[str] = [] 

@app.get("/") 
async def read_root():
    return FileResponse('static/index.html')

@app.post("/secure_chat")
async def chat(request: ChatRequest):
    # 1. Redact Secrets Locally
    clean_prompt, entity_map = protect_prompt(request.prompt, request.custom_secrets)
    
    print(f"🔒 Original: {request.prompt}")
    print(f"🛡️  Sent to Cloud: {clean_prompt}")
    
    ai_text = "Error: All AI models are currently busy or out of quota."

    # --- ROBUST MODEL SWITCHER ---
    # If one model fails (429 Quota Exceeded), it instantly tries the next one.
    available_models = [
        "gemini-2.5-flash",       # Standard Flash (Higher limits)
        "gemini-2.0-flash",       # Previous Flash (Very stable)
        "gemini-1.5-flash",       # Older reliable Flash
        "gemini-2.5-flash-lite",  # Lite version (Low quota, keep as backup)
        "gemini-pro"              # Standard Pro
    ]

    for model_name in available_models:
        try:
            print(f"🔄 Trying model: {model_name}...")
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(clean_prompt)
            ai_text = response.text
            print(f"✅ Success with {model_name}!")
            break # Stop the loop, we got an answer!
        except Exception as e:
            print(f"⚠️ {model_name} failed: {e}")
            # Loop continues to the next model automatically...
    
    # 3. Restore Secrets Locally
    final_response = restore_response(ai_text, entity_map)
    
    return {
        "response": final_response,
        "privacy_metadata": {
            "sanitized_prompt": clean_prompt,
            "secrets_hidden": len(entity_map)
        }
    }

@app.post("/upload_file")
async def upload_document(
    file: UploadFile = File(...), 
    custom_secrets: str = Form("")
):
    content = await file.read()
    filename = file.filename.lower()
    
    # Clean secrets list
    secret_list = [s.strip() for s in custom_secrets.split(',') if s.strip()]
    
    safe_text = ""
    secret_count = 0

    try:
        # 1. PDF Handling
        if filename.endswith('.pdf'):
            safe_text, secret_count = process_pdf_with_secrets(content, secret_list)
        
        # 2. IMAGE Handling
        elif filename.endswith(('.png', '.jpg', '.jpeg', '.bmp')):
            safe_text, secret_count = process_image(content, secret_list)

        # 3. TEXT Handling
        elif filename.endswith(('.txt', '.md', '.py', '.js', '.html', '.json', '.csv')):
            text_content = content.decode('utf-8', errors='ignore')
            safe_text, entity_map = protect_prompt(text_content, custom_secrets=secret_list)
            secret_count = len(entity_map)
        
        else:
            return {"filename": filename, "safe_content": "[Unsupported File Format]", "secrets_removed": 0}

        return {
            "filename": file.filename,
            "safe_content": safe_text,
            "secrets_removed": secret_count
        }
    except Exception as e:
        print(f"Processing Error: {e}")
        return {"filename": filename, "safe_content": f"Error: {str(e)}", "secrets_removed": 0}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)