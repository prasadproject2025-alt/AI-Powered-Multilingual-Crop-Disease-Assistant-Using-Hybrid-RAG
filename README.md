# 🌾 AI-Powered Multilingual Crop Disease Assistant Using Hybrid RAG

An intelligent, full-stack agricultural advisory web application designed to assist rural farmers in diagnosing crop diseases, recognizing nutrient deficiencies, and obtaining actionable corrective measures. 

The system implements a **Hybrid Retrieval-Augmented Generation (RAG)** architecture powered by the **Google Gemini API**, grounding conversational AI with a local expert-vetted knowledge base. To ensure accessibility for low-literacy and linguistically diverse farming communities, the application natively supports text and voice interactions across **11 regional Indian languages**.

---

## 🚀 Core Features

*   **Hybrid RAG Architecture:** Combines semantic/fuzzy string matching over a local "ground-truth" database with the generative capability of Large Language Models (LLMs) to eliminate hallucinations.
*   **11 Regional Languages Supported:** English, Hindi (हिन्दी), Telugu (తెలుగు), Tamil (தமிழ்), Kannada (ಕನ್ನಡ), Marathi (मराठी), Bengali (বাংলা), Gujarati (ગુજરાતી), Malayalam (മലയാളം), Odia (ଓଡ଼ିଆ), and Punjabi (ਪੰਜਾਬੀ).
*   **Multimodal Voice Pipeline:** Real-time **Speech-to-Text (STT)** via browser-native Web Speech API and backend-driven, high-fidelity **Text-to-Speech (TTS)** via Google Text-to-Speech (`gTTS`).
*   **Linguistic Normalization:** Bi-directional inbound translation engine standardizes multilingual queries to English for precise backend search matching.
*   **Dynamic Knowledge Insight Panel:** A client-side parser that dynamically extracts and displays structured metadata (Crop, Predicted Disease, Symptoms summary, Remedies) from conversational outputs.
*   **Structured 3-Section Framework:** Responses are strictly engineered into standard, farmer-friendly sections: Crop & Condition, Symptoms Noticed, and Recommended Actions.

---

## 🛠️ Technology Stack

### Frontend (Client Layer)
*   **Languages:** HTML5, CSS3, JavaScript (ES6+)
*   **Typography:** Google Fonts (Nunito Integration for regional script readability)
*   **Voice Input Engine:** Web Speech API (`webkitSpeechRecognition`)
*   **Media Pipeline:** HTML5 Audio API (Blob URL Streaming)

### Backend (Orchestration Layer)
*   **Framework:** Python Framework (Flask)
*   **Cross-Origin Policy:** `Flask-CORS`

### AI & Data Engine
*   **Core LLM Engine:** Google Generative AI API (`gemini-2.5-flash` / `gemini-2.0-flash`)
*   **Data Processing:** `pandas` (Knowledge Base indexer)
*   **Fuzzy Search Engine:** `rapidfuzz` (Token Set Ratio algorithmic matching)
*   **Translation Bridge:** `translators` library (Google Translation Engine backend wrapper)
*   **Voice Synthesis Engine:** `gTTS` (Google Text-to-Speech API)

---

## 📂 Project Structure

```text
CropAssistant/
│
├── utils/
│   ├── __init__.py               # Utility package definitions
│   ├── gemini_integration.py     # Gemini API config & Master System Prompt
│   ├── kb_search.py              # Synonym mapping & RapidFuzz logic over CSV
│   └── translator.py             # Inbound/Outbound translation bridging
│
├── app.py                        # Main Flask server hosting /chat and /tts endpoints
├── app.js                        # Frontend controller managing UI, STT logic, & Fetch streams
├── index.html                    # Responsive 3-panel UI layout dashboard
├── styles.css                    # Fluid UI design, grid structures, & animated gradients
└── crop_kb.csv                   # Local Expert-Vetted Factual Reference Database

```

---

## ⚙️ System Workflow Pipeline

1. **Ingestion:** The farmer triggers voice recording or types an input in a chosen regional tongue (e.g., Tamil).
2. **Linguistic Normalization:** The Flask backend translates the query to English using the `translators` module.
3. **Factual Retrieval (R):**
* The `kb_search` engine applies **Synonym Mapping** (e.g., converts "paddy" to "rice").
* `rapidfuzz` calculates similarity matrices between input tokens and the `crop_kb.csv` symptom corpus.
* Rows scoring above a $75\%$ confidence threshold are cached as localized grounding facts.


4. **Prompt Augmentation (A):** Factual constraints and the English-translated conversational history are dynamically injected into a highly conditioned structural prompt.
5. **Contextual Generation (G):** The **Gemini API** evaluates the prompt under strict rule priorities, reasoning out a custom, localized output directly in the targeted script.
6. **Streaming Synthesis:** When the playback action is caught, the response is parsed through backend `gTTS`, streamed back as an in-memory `audio/mpeg` Byte stream, and executed via the client-side Audio engine.

---

## 🔧 Setup & Installation

### Prerequisites

* Python 3.10 or higher
* Google Gemini API Key (Obtained via Google AI Studio)
* A modern web browser with active microphone access permissions (Chrome/Edge/Safari recommended for Web Speech API compatibility)

### 1. Clone the Project & Set Up Environment

```bash
git clone [https://github.com/your-username/multilingual-crop-assistant.git](https://github.com/your-username/multilingual-crop-assistant.git)
cd multilingual-crop-assistant

# Create a virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

```

### 2. Install Required Python Packages

```bash
pip install Flask flask-cors pandas rapidfuzz google-generativeai translators gTTS

```

### 3. Backend Code Configurations

Open `app.py` and modify the following placeholders with your technical specifications:

```python
# 1. Provide your unique Gemini API Key
GEMINI_API_KEY = 'YOUR_ACTUAL_GEMINI_API_KEY_HERE'

# 2. Update to the exact file path where your crop_kb.csv resides
KB_PATH = r"C:\path\to\your\folder\crop_kb.csv"

```

---

## 🚀 Running the Application

### 1. Launch the Flask Backend Server

With your virtual environment active, execute:

```bash
python app.py

```

The server will boot locally at `http://127.0.0.1:5000/` and begin caching the Knowledge Base.

### 2. Launch the Web Client

Since the frontend interacts over standard local ports via the Fetch API, you can simply open the `index.html` file directly in your preferred web browser, or serve it using a lightweight Live Server extension in your editor.

---

## 📝 Knowledge Base (`crop_kb.csv`) Design Standard

Ensure your local database file matches the structural columns specified below (comma-separated, row-normalized):

```csv
Crop,Disease,Symptoms,Solution
rice,nitrogen deficiency,leaves turning light green or yellow starting from older leaves stunted growth,apply nitrogenous fertilizers like urea split application across growth phases check soil ph
tomato,early blight,concentric dark rings target spots on older leaves yellow halos around spots fruit rot,spray chemical fungicides like mancozeb prune lower infected foliage maintain proper row spacing

```

## 👨‍💻 Author

**Akash K**

M.Tech Software Engineering

Developed in partial fulfillment of the course requirements for Artificial Intelligence – SWE4010

GitHub: https://github.com/Akash2027

LinkedIn: www.linkedin.com/in/akash-k-bb9a20274

---

## ⭐ Support

If you found this project useful, consider giving the repository a star.

Your support helps improve and maintain future AI and RAG based projects.
