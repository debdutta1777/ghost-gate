# 👻 Ghost-Gate | Interstellar Privacy Layer

![Status](https://img.shields.io/badge/Status-Operational-success)
![Security](https://img.shields.io/badge/Security-Zero%20Trust-blueviolet)
![AI](https://img.shields.io/badge/AI-Gemini%202.5%20Flash-orange)

**Ghost-Gate** is a "Zero-Trust" privacy firewall that sits between you and public AI models (like Google Gemini). It intercepts your messages, **redacts sensitive data locally** (PII, API keys, custom secrets), and only sends the sanitized version to the cloud. When the AI replies, Ghost-Gate **restores the original data** instantly.

**"Your data never leaves your atmosphere."**

---

## 🌟 Key Features

### 🛡️ **Zero-Trust Redaction Engine**
- **Automated PII Scanning:** Instantly detects and hides Names, Emails, Phone Numbers, and US SSNs using **Microsoft Presidio**.
- **Custom Deny List:** Manually specify secret project names (e.g., "Project Apollo") to hide them from the AI.
- **Local Restoration:** The AI says `<PERSON_1>`, but you see **John Doe**. The mapping table never leaves your RAM.

### 👁️ **Ghost Vision (OCR)**
- Upload screenshots, invoices, or documents (PNG/JPG).
- **Tesseract OCR** extracts the text locally.
- Redacts sensitive info from the *pixels* before the AI analyzes it.

### 🧠 **Robust AI Core**
- **Self-Healing Connection:** Automatically switches models (`Flash` → `Flash-Lite` → `Pro`) if Google's API quota is exceeded (429 Errors).
- **Context-Aware:** Handles multi-turn conversations and file attachments (PDFs, Code, Images).

### 🎨 **"Interstellar" UI**
- Fully responsive **Quantum/Sci-Fi Interface**.
- **Visuals:** Animated Nebula backgrounds, Holographic Data Grids, and Quantum Particles.
- **Audio Feedback:** Interactive sci-fi bleeps and bloops for user actions.

---

## 🛠️ Tech Stack

- **Backend:** Python, FastAPI, Uvicorn
- **Frontend:** HTML5, CSS3 (Glassmorphism), Vanilla JS
- **AI Model:** Google Gemini (via `google-generativeai`)
- **Security:** Microsoft Presidio (`presidio-analyzer`), RegEx
- **OCR:** Tesseract (`pytesseract`), Pillow
- **PDF:** `pypdf`

---

## 🚀 Installation

### 1. Prerequisites
- **Python 3.9+**
- **Tesseract OCR** (Required for Image Analysis)
  - *Windows:* [Download Installer](https://github.com/UB-Mannheim/tesseract/wiki) (Install to `C:\Program Files\Tesseract-OCR`)
  - *Mac:* `brew install tesseract`

### 2. Clone & Setup
```bash
git clone [https://github.com/yourusername/ghost-gate.git](https://github.com/yourusername/ghost-gate.git)
cd ghost-gate

# Create Virtual Environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\Activate

# Activate (Mac/Linux)
source venv/bin/activate

-----
