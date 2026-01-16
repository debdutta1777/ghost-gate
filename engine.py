import io
import re
from pypdf import PdfReader
from PIL import Image
import pytesseract
from presidio_analyzer import AnalyzerEngine

# 1. Initialize Engines
analyzer = AnalyzerEngine()

# 2. Configure Tesseract Path (Windows)
# If Tesseract is in your system PATH, you can remove this line.
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def protect_prompt(text: str, custom_secrets: list = None):
    """
    1. Replaces Custom Secrets (e.g., 'Project X') -> <CONFIDENTIAL_1>
    2. Replaces URLs (LinkedIn, GitHub) -> <LINK_1>
    3. Replaces Standard PII (Names, Phones) -> <PERSON_...>, <PHONE_...>
    """
    entity_map = {}
    
    # --- PHASE 1: CUSTOM SECRETS ---
    if custom_secrets:
        for secret in custom_secrets:
            if not secret.strip():
                continue
            if secret.lower() in text.lower():
                placeholder = f"<CONFIDENTIAL_{len(entity_map) + 1}>"
                pattern = re.compile(re.escape(secret), re.IGNORECASE)
                text = pattern.sub(placeholder, text)
                entity_map[placeholder] = secret

    # --- PHASE 2: URL REDACTION ---
    # Catches http://, https://, and www. links
    url_pattern = re.compile(r'(https?://\S+|www\.\S+)', re.IGNORECASE)
    found_urls = list(set(url_pattern.findall(text))) # Get unique URLs

    for url in found_urls:
        placeholder = f"<LINK_{len(entity_map) + 1}>"
        text = text.replace(url, placeholder)
        entity_map[placeholder] = url

    # --- PHASE 3: STANDARD PII ---
    results = analyzer.analyze(
        text=text, 
        entities=["PERSON", "PHONE_NUMBER", "EMAIL_ADDRESS", "US_SSN", "CREDIT_CARD"], 
        language='en'
    )

    # Sort results in REVERSE order to prevent index shifting during replacement
    results.sort(key=lambda x: x.start, reverse=True)

    for result in results:
        original_value = text[result.start:result.end]
        placeholder = f"<{result.entity_type}_{len(entity_map) + 1}>"
        entity_map[placeholder] = original_value
        text = text[:result.start] + placeholder + text[result.end:]

    return text, entity_map

def restore_response(text: str, entity_map: dict):
    """
    Swaps tokens back to real data.
    """
    for placeholder, original_value in entity_map.items():
        text = text.replace(placeholder, f"**{original_value}**")
    return text

def process_pdf_with_secrets(file_bytes, custom_secrets):
    """
    Reads a PDF and sanitizes it using a specific list of secrets.
    """
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        full_text = ""
        
        for page in reader.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"
        
        # Pass the secrets here!
        safe_text, entity_map = protect_prompt(full_text, custom_secrets=custom_secrets)
        return safe_text, len(entity_map)
        
    except Exception as e:
        print(f"PDF Error: {e}")
        return "Error reading PDF file.", 0

def process_pdf(file_bytes):
    """
    Wrapper for backward compatibility (defaults to no custom secrets).
    """
    return process_pdf_with_secrets(file_bytes, [])

def process_image(file_bytes, custom_secrets):
    """
    Reads an image (PNG/JPG), extracts text via OCR, and sanitizes it.
    """
    try:
        # Convert bytes to Image
        image = Image.open(io.BytesIO(file_bytes))
        
        # Extract Text
        raw_text = pytesseract.image_to_string(image)
        
        # Sanitize
        safe_text, entity_map = protect_prompt(raw_text, custom_secrets=custom_secrets)
        
        return safe_text, len(entity_map)
        
    except Exception as e:
        print(f"OCR Error: {e}")
        return "Error analyzing image. Ensure Tesseract OCR is installed.", 0