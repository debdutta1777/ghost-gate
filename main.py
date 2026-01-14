from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from engine import protect_prompt, restore_response
import uvicorn

app = FastAPI(title="Ghost-Gate")

# Mounts the static folder so CSS/JS works
app.mount("/static", StaticFiles(directory="static"), name="static")

class ChatRequest(BaseModel):
    prompt: str

@app.get("/") 
async def read_root():
    return FileResponse('static/index.html')

@app.post("/secure_chat")
async def chat(request: ChatRequest):
    # 1. Sanitize
    clean_prompt, entity_map = protect_prompt(request.prompt)

    print(f"🔒 Original: {request.prompt}")
    print(f"🛡️  Sent to Cloud: {clean_prompt}")

    # 2. Simulate AI
    ai_response = f"I have processed the records for {clean_prompt}. The status is confirmed."

    # 3. Restore
    final_response = restore_response(ai_response, entity_map)

    return {
        "response": final_response,
        "privacy_metadata": {
            "sanitized_prompt": clean_prompt,
            "secrets_hidden": len(entity_map)
        }
    }

if __name__ == "__main__":
    # Uses 127.0.0.1 so the link in VS Code is clickable
    uvicorn.run(app, host="127.0.0.1", port=8000)