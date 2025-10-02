# Appointify 🩺🤖  
**AI-Powered Appointment Scheduler Assistant**

Appointify is a backend system designed to simplify appointment scheduling using **AI-powered entity recognition, OCR, and natural language processing**.  
It extracts and normalizes appointment details such as **date, time, and department** from text or image inputs, and returns structured JSON for seamless integration.

---

## 🚀 Features
- Extracts **appointment details** (date, time, department) from raw text.
- Supports **OCR (Optical Character Recognition)** to parse text from uploaded images.
- Uses **NLP (Gemini/LLM)** for entity recognition.
- Provides structured **JSON response** for frontend integration.
- Handles **ambiguity detection** with a `needs_clarification` response.

---

## 📂 Project Structure
```
Appointify/
├── main.py            # Main Flask application and API routes
├── requirements.txt   # Project dependencies
├── .env               # Environment variables (e.g., API keys)
└── utils/
    ├── appointment.py # Final JSON assembly logic for structured appointment response
    ├── ner.py         # Named Entity Recognition (date, time, department extraction)
    ├── ocr.py         # OCR module for extracting text from images
    └── normalize.py   # Normalization of extracted entities (date, time, department)
```

---

## ⚙️ Installation & Setup

```bash
# 1. Clone the repository
git clone https://github.com/meenakshi3151/Appointify.git
cd Appointify

# 2. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate   # On macOS/Linux
# venv\Scripts\activate    # On Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set environment variables
# Create a .env file in the root directory and add:
# GEMINI_API_KEY=your_api_key_here

# 5. Run the Flask server
python main.py

