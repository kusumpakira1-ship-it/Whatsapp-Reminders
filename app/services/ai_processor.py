import json
import base64
import requests
import typing_extensions as typing
from core.config import settings
import re
import google.generativeai as genai
from PIL import Image
import io

try:
    import pypdf
except ImportError:
    pypdf = None

# Configure Gemini API if configured
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)

class FarmExtraction(typing.TypedDict):
    shead_name: str
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
Your job is to read user messages (in English, Hindi, Telugu, Tamil, Kannada, Malayalam, broken English, or SMS shorthand) or document content (such as PDFs/images)
and extract all relevant farm records into a clean, structured JSON format containing a list of records.

RULES:
1. Translate everything into clean English.
2. Identify the shead name if mentioned (e.g., 'shead3' or 'shead 3' -> 'Shead 3'). If not mentioned, use empty string.
3. Classify into ONE category per record: egg, feed, medicine, mortality, sales, purchase, expense, unknown.
4. Extract quantity as a number.
5. Extract unit (trays, bags, kg, pieces, rupees).
6. Extract monetary amount as a float. If a calculation is provided (e.g., '100 * 5'), perform the math and store the total. If none, use 0.0.
7. Any additional dynamic or custom fields (like date, invoice number, vehicle number, customer name) should be formatted and appended to the 'notes' field (e.g., "Invoice: 123, Vehicle: AP39").
8. Store the translated, clean English version in 'processed_text'.
9. Estimate your confidence (0.0 to 1.0) in 'confidence_score'.
10. If the input describes MULTIPLE transactions, items, days, or rows, extract EACH of them as a separate item in the 'records' list.
11. If the input is a single transaction, the 'records' list must contain exactly one record item.
12. YOU MUST ONLY RETURN VALID JSON. NO MARKDOWN. NO CODE BLOCKS. NO OTHER TEXT.

EXPECTED JSON SCHEMA:
{
  "records": [
    {
      "shead_name": "string",
      "category": "string",
      "quantity": number,
      "unit": "string",
      "amount": number,
      "notes": "string",
      "confidence_score": number,
      "processed_text": "string"
    }
  ]
}

EXAMPLES:
"250 ట్రేలు వచ్చాయి" -> {"records": [{"shead_name":"", "category":"egg", "quantity":250, "unit":"trays", "amount":0.0, "notes":"", "confidence_score": 0.95, "processed_text": "250 trays received"}]}
"Shead 1 sold 100 trays at 520. Shead 2 sold 50 trays at 520." -> {
  "records": [
    {"shead_name":"Shead 1", "category":"sales", "quantity":100, "unit":"trays", "amount":520.0, "notes":"", "confidence_score": 0.98, "processed_text": "Shead 1 sold 100 trays at 520"},
    {"shead_name":"Shead 2", "category":"sales", "quantity":50, "unit":"trays", "amount":520.0, "notes":"", "confidence_score": 0.98, "processed_text": "Shead 2 sold 50 trays at 520"}
  ]
}
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

def _call_gemini(prompt: str, images: list = None) -> dict:
    if not settings.GEMINI_API_KEY:
        print("Gemini API Key is not configured in environment variables.")
        return None
        
    try:
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=get_system_prompt(),
            generation_config={"response_mime_type": "application/json"}
        )
        
        contents = []
        if images:
            for img_b64 in images:
                try:
                    img_data = base64.b64decode(img_b64)
                    img = Image.open(io.BytesIO(img_data))
                    contents.append(img)
                except Exception as e:
                    print(f"Failed to load image in Gemini: {e}")
        
        contents.append(prompt)
        response = model.generate_content(contents)
        response_text = response.text
        
        # Clean up possible markdown code blocks if Gemini still outputs them
        response_text = re.sub(r'```json\n?', '', response_text)
        response_text = re.sub(r'```\n?', '', response_text)
        
        return json.loads(response_text)
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return None

def _call_ai(prompt: str, images: list = None, is_vision: bool = False) -> dict:
    provider = settings.AI_PROVIDER.lower()
    if provider == "gemini":
        print("Using Gemini API for processing...")
        return _call_gemini(prompt, images)
    else:
        print("Using Ollama API for processing...")
        return _call_ollama(prompt, images, is_vision)

def process_text(text: str) -> dict:
    """Processes plain text using the configured AI provider."""
    prompt = f"Extract data from this message:\n{text}"
    result = _call_ai(prompt)
    
    if result:
        return result
    return _fallback_dummy_response(text)

def process_image(image_path: str, caption: str = "") -> dict:
    """Processes images (OCR + Understanding) using configured AI provider."""
    try:
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        
        prompt = "Extract farm data from this image. If there are calculations written in the image (like quantity * price), perform the math to find the total amount."
        if caption:
            prompt += f" The user also provided this caption: {caption}"
            
        result = _call_ai(prompt, images=[encoded_string], is_vision=True)
        if result:
            return result
    except Exception as e:
        print(f"AI Image Pre-Processing Error: {e}")
        
    return _fallback_dummy_response(caption or "Image processing failed")

def process_document(doc_path: str, caption: str = "") -> dict:
    """Processes documents (PDFs) by extracting text and sending to configured AI provider."""
    if not pypdf:
        print("pypdf is not installed. Cannot process PDF.")
        return _fallback_dummy_response(caption or "PDF processing not supported")
        
    try:
        # Extract text from PDF
        reader = pypdf.PdfReader(doc_path)
        extracted_text = ""
        for page in reader.pages:
            extracted_text += page.extract_text() or ""
            
        if not extracted_text.strip():
            print("No text found in PDF.")
            return _fallback_dummy_response(caption or "Empty PDF")
            
        # Send extracted text to AI
        prompt = f"Extract the relevant farm data summary from this document text:\n{extracted_text}"
        if caption:
            prompt += f"\nUser caption: {caption}"
            
        result = _call_ai(prompt)
        if result:
            return result
    except Exception as e:
        print(f"AI Document Processing Error: {e}")
        
    return _fallback_dummy_response(caption or "Document processing failed")

def _fallback_dummy_response(text: str) -> dict:
    """Fallback if Ollama fails or is unreachable."""
    return {
        "records": [
            {
                "shead_name": "",
                "category": "unknown",
                "quantity": 0,
                "unit": "",
                "amount": 0.0,
                "notes": "Ollama processing failed or unreachable",
                "confidence_score": 0.0,
                "processed_text": text
            }
        ]
    }
