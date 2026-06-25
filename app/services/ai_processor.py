import json
import base64
import requests
import typing_extensions as typing
from core.config import settings
import re

# We will optionally import PyMuPDF inside the document processor to keep it isolated
try:
    import fitz # PyMuPDF
except ImportError:
    fitz = None

class FarmExtraction(typing.TypedDict):
    farm_name: str
    category: str
    quantity: float
    unit: str
    amount: float
    notes: str
    confidence_score: float
    processed_text: str

def get_system_prompt() -> str:
    return """
You are a specialized agricultural data extraction AI.
Your job is to read user messages (in English, Hindi, Telugu, Tamil, Kannada, Malayalam, broken English, or SMS shorthand) 
and extract the farm data into a clean, structured JSON format.

RULES:
1. Translate everything into clean English.
2. Identify the farm name if mentioned (e.g., 'frm3' -> 'Farm 3'). If not mentioned, return empty string.
3. Classify into ONE category: egg, feed, medicine, mortality, sales, purchase, expense, unknown.
4. Extract quantity as a number.
5. Extract unit (trays, bags, kg, pieces, rupees).
6. Extract monetary amount as a float if mentioned (e.g., 'sold for 520', 'price 200'). If none, use 0.0.
7. Store the translated, clean English version in 'processed_text'.
8. Estimate your confidence (0.0 to 1.0).
9. YOU MUST ONLY RETURN VALID JSON. NO MARKDOWN. NO CODE BLOCKS. NO OTHER TEXT.

EXPECTED JSON SCHEMA:
{
  "farm_name": "string",
  "category": "string",
  "quantity": number,
  "unit": "string",
  "amount": number,
  "notes": "string",
  "confidence_score": number,
  "processed_text": "string"
}

EXAMPLES:
"250 ట్రేలు వచ్చాయి" -> {"farm_name":"", "category":"egg", "quantity":250, "unit":"trays", "amount":0.0, "notes":"", "confidence_score": 0.95, "processed_text": "250 trays received"}
"Farm 1 sold 100 trays at 520" -> {"farm_name":"Farm 1", "category":"sales", "quantity":100, "unit":"trays", "amount":520.0, "notes":"", "confidence_score": 0.98, "processed_text": "Farm 1 sold 100 trays at 520"}
"""

def _call_ollama(prompt: str, images: list = None, is_vision: bool = False) -> dict:
    url = f"{settings.OLLAMA_URL}/api/generate"
    model = settings.OLLAMA_VISION_MODEL if is_vision else settings.OLLAMA_MODEL
    
    payload = {
        "model": model,
        "system": get_system_prompt(),
        "prompt": prompt,
        "stream": False,
        "format": "json"  # Ollama 0.1.30+ supports native JSON formatting
    }
    
    if images:
        payload["images"] = images

    try:
        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()
        result = response.json()
        response_text = result.get("response", "")
        
        # Clean up possible markdown code blocks if Ollama still outputs them
        response_text = re.sub(r'```json\n?', '', response_text)
        response_text = re.sub(r'```\n?', '', response_text)
        
        return json.loads(response_text)
    except requests.exceptions.RequestException as e:
        print(f"Ollama API Connection Error: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Ollama JSON Parsing Error: {e}\nRaw Response: {response_text}")
        return None
    except Exception as e:
        print(f"Ollama Unexpected Error: {e}")
        return None

def process_text(text: str) -> dict:
    """Processes plain text using Ollama."""
    prompt = f"Extract data from this message:\n{text}"
    result = _call_ollama(prompt)
    
    if result:
        return result
    return _fallback_dummy_response(text)

def process_image(image_path: str, caption: str = "") -> dict:
    """Processes images (OCR + Understanding) using Ollama Vision Model (llava)."""
    try:
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        
        prompt = "Extract farm data from this image."
        if caption:
            prompt += f" The user also provided this caption: {caption}"
            
        result = _call_ollama(prompt, images=[encoded_string], is_vision=True)
        if result:
            return result
    except Exception as e:
        print(f"AI Image Pre-Processing Error: {e}")
        
    return _fallback_dummy_response(caption or "Image processing failed")

def process_document(doc_path: str, caption: str = "") -> dict:
    """Processes documents (PDFs) by extracting text and sending to Ollama."""
    if not fitz:
        print("PyMuPDF is not installed. Cannot process PDF.")
        return _fallback_dummy_response(caption or "PDF processing not supported")
        
    try:
        # Extract text from PDF
        doc = fitz.open(doc_path)
        extracted_text = ""
        for page in doc:
            extracted_text += page.get_text()
            
        if not extracted_text.strip():
            print("No text found in PDF.")
            return _fallback_dummy_response(caption or "Empty PDF")
            
        # Send extracted text to Ollama
        prompt = f"Extract the relevant farm data summary from this document text:\n{extracted_text}"
        if caption:
            prompt += f"\nUser caption: {caption}"
            
        result = _call_ollama(prompt)
        if result:
            return result
    except Exception as e:
        print(f"AI Document Processing Error: {e}")
        
    return _fallback_dummy_response(caption or "Document processing failed")

def _fallback_dummy_response(text: str) -> dict:
    """Fallback if Ollama fails or is unreachable."""
    return {
        "farm_name": "",
        "category": "unknown",
        "quantity": 0,
        "unit": "",
        "amount": 0.0,
        "notes": "Ollama processing failed or unreachable",
        "confidence_score": 0.0,
        "processed_text": text
    }
