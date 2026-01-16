import os
import google.generativeai as genai
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from engine import protect_prompt, restore_response, process_pdf
import uvicorn

# 1. Load the Secret Key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ ERROR: No API Key found in .env file!")
else:
    # Use the model that worked for you
    genai.configure(api_key=api_key)
    print("✅ Gemini AI Connected")

app = FastAPI(title="Ghost-Gate")

app.mount("/static", StaticFiles(directory="static"), name="static")

class ChatRequest(BaseModel):
    prompt: str
    custom_secrets: list[str] = [] 

@app.get("/") 
async def read_root():
    return FileResponse('static/index.html')

@app.post("/secure_chat")
async def chat(request: ChatRequest):
    clean_prompt, entity_map = protect_prompt(request.prompt, request.custom_secrets)
    
    print(f"🔒 Original: {request.prompt}")
    print(f"🛡️  Sent to Cloud: {clean_prompt}")
    
    try:
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
        response = model.generate_content(clean_prompt)
        ai_text = response.text
    except Exception as e:
        ai_text = f"Error connecting to AI: {str(e)}"
    
    final_response = restore_response(ai_text, entity_map)
    
    return {
        "response": final_response,
        "privacy_metadata": {
            "sanitized_prompt": clean_prompt,
            "secrets_hidden": len(entity_map)
        }
    }

@app.post("/upload_pdf")
async def upload_document(file: UploadFile = File(...)):
    # 1. Read the uploaded file
    content = await file.read()
    
    # 2. Process it through our Engine
    safe_text, secret_count = process_pdf(content)
    
    # 3. Return the clean text
    return {
        "filename": file.filename,
        "safe_content": safe_text,
        "secrets_removed": secret_count
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)