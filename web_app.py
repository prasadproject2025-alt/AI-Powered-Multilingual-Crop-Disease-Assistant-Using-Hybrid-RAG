from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import uvicorn
import os

# Import utilities (use the correct function names)
from utils.gemini_integration import generate_response
from utils.kb_search import search_kb
from utils.translator import translate_text

# Initialize FastAPI app
app = FastAPI(title="AI-Powered Multilingual Crop Disease Assistant")

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static frontend
app.mount("/static", StaticFiles(directory="web"), name="static")

# Load knowledge base
KB_PATH = r"C:\Users\akash\Desktop\crop chatbot project\crop_kb.csv"
kb_df = pd.read_csv(KB_PATH) if os.path.exists(KB_PATH) else pd.DataFrame()

@app.get("/")
async def serve_index():
    """Serve the frontend."""
    return FileResponse("web/index.html")

@app.post("/api/ask")
async def ask_crop_assistant(request: Request):
    """Main API endpoint for multilingual crop disease queries."""
    try:
        data = await request.json()
        query = data.get("query", "").strip()
        lang = data.get("language", "en")

        if not query:
            return JSONResponse({"error": "Empty query"}, status_code=400)

        # Translate input to English if necessary
        query_en = translate_text(query, "en") if lang != "en" else query

        # Search in knowledge base
        kb_result = search_kb(query_en, kb_df)

        # Construct AI prompt
        prompt = f"""
        Farmer Query: {query_en}
        Knowledge Base Result: {kb_result}

        Generate a farmer-friendly explanation of the crop disease,
        including cause, symptoms, and prevention/treatment methods.
        Keep it short, simple, and educational.
        """

        # Generate Gemini response
        ai_response_en = generate_response(prompt)

        # Translate AI response to farmer's language
        ai_response_final = (
            translate_text(ai_response_en, lang) if lang != "en" else ai_response_en
        )

        return JSONResponse({
            "query": query,
            "response": ai_response_final,
            "kb_match": kb_result,
            "language": lang
        })

    except Exception as e:
        # Print server-side error for debugging
        print(f"❌ Internal Server Error: {e}")
        return JSONResponse(
            {"error": f"Internal Server Error: {str(e)}"},
            status_code=500
        )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
