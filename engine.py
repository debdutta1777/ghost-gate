import io
import re
from pypdf import PdfReader
from presidio_analyzer import AnalyzerEngine
# We don't need AnonymizerEngine anymore since we will handle replacements manually

# Initialize Engine
analyzer = AnalyzerEngine()

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

    # --- PHASE 2: URL REDACTION (NEW!) ---
    # We catch links BEFORE Presidio because links often contain names
    # Catches http://, https://, and www. links
    url_pattern = re.compile(r'(https?://\S+|www\.\S+)', re.IGNORECASE)
    found_urls = list(set(url_pattern.findall(text))) # Get unique URLs

    for url in found_urls:
        placeholder = f"<LINK_{len(entity_map) + 1}>"
        # Use simple replace for speed and safety
        text = text.replace(url, placeholder)
        entity_map[placeholder] = url

    # --- PHASE 3: STANDARD PII ---
    # Analyze the text to find where the secrets are
    results = analyzer.analyze(
        text=text, 
        entities=["PERSON", "PHONE_NUMBER", "EMAIL_ADDRESS", "US_SSN", "CREDIT_CARD"], 
        language='en'
    )

    # Sort results in REVERSE order (end to start) to prevent index shifting
    results.sort(key=lambda x: x.start, reverse=True)

    for result in results:
        # 1. Grab the original text (e.g., "John Doe")
        original_value = text[result.start:result.end]
        
        # 2. Create a unique tag (e.g., <PERSON_5>)
        placeholder = f"<{result.entity_type}_{len(entity_map) + 1}>"
        
        # 3. Store the mapping
        entity_map[placeholder] = original_value
        
        # 4. Replace it in the string
        text = text[:result.start] + placeholder + text[result.end:]

    return text, entity_map

def restore_response(text: str, entity_map: dict):
    """
    Swaps tokens back to real data.
    """
    for placeholder, original_value in entity_map.items():
        text = text.replace(placeholder, f"**{original_value}**")
    return text

def process_pdf(file_bytes):
    """
    Reads a PDF, extracts text, and sanitizes it.
    """
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        full_text = ""
        
        for page in reader.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"
        
        # Sanitize the text (Empty custom secrets list for auto-scan)
        safe_text, entity_map = protect_prompt(full_text, custom_secrets=[])
        
        return safe_text, len(entity_map)
        
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return "Error reading PDF file.", 0