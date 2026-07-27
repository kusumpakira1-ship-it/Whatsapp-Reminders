import json
import base64
import requests
import typing_extensions as typing
from config import settings
import re
import google.generativeai as genai
from PIL import Image
import io

try:
    import pypdf
except ImportError:
    pypdf = None

try:
    import pytesseract
except ImportError:
    pytesseract = None

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

def get_system_prompt(provider: str = "gemini") -> str:
    if provider == "ollama":
        return r"""You are a specialized poultry farm data extraction AI. You read user messages and output a valid JSON object or a JSON array of objects.
EXPECTED JSON SCHEMA:
{
  "shead_name": "string (e.g. 'Shead 3', 'Chick Whites', 'Chick Brownie')",
  "category": "string (exactly one of: 'egg_collection_1', 'egg_collection_2', 'egg_collection', 'hen_weight', 'mortality', 'egg_loaded', 'egg_unloaded', 'production', 'sales', 'feed', 'raw_material', 'medicine', 'expense', 'purchase', 'unknown')",
  "quantity": number,
  "unit": "string (e.g. 'trays', 'eggs', 'kg', 'bags')",
  "amount": number,
  "notes": "string",
  "confidence_score": number (0.0 to 1.0),
  "processed_text": "string (English translation)"
}
Rules:
1. Multiple entries: If the message contains entries for multiple sheds or categories, output a JSON array of objects (one for each shed/entry).
2. Chick mortality: If the message lists separate mortality for Whites and Brownie (e.g. "Chick Whites: 2, Brownie: 1"), output two separate objects with shead_name as 'Chick Whites' and 'Chick Brownie' under category 'mortality'.
3. Hen weight: E.g. "Shead 1 bird weight: 1.516" or "Shead 1 weight 1.516" -> category: 'hen_weight', shead_name: 'Shead 1', quantity: 1.516, unit: 'kg'.
4. Feed consumption: E.g. "Shead 1 feed 110" -> category: 'feed', shead_name: 'Shead 1', quantity: 110, unit: 'bags' (or 'kg').
5. NO CODE BLOCKS, NO MARKDOWN. ONLY JSON OR JSON ARRAY."""

    return r"""You are a specialized poultry farm data extraction AI. You read WhatsApp messages from farm supervisors and extract farm records into a clean, structured JSON object or a JSON array of objects (if multiple entries are reported).
Use EXACTLY ONE of these category values:
  egg_collection_1 -> MORNING collection (keywords: 1st, morning, subah, batch 1, round 1)
  egg_collection_2 -> EVENING collection (keywords: 2nd, evening, shaam, batch 2, round 2)
  egg_collection   -> General egg collection (when round is not specified)
  hen_weight       -> Bird weight measurements (e.g. "Shead 1 bird weight 1.516" -> quantity: 1.516, unit: 'kg')
  mortality        -> Bird deaths (keywords: died, death, dead, mortality)
  egg_loaded       -> Eggs loaded/dispatched/sent out
  egg_unloaded     -> Eggs unloaded/received back
  production       -> Flock stats: bird count, age
  sales            -> Egg sale revenue
  feed             -> Feed given/consumed (e.g. "Shead 1 feed 110" -> quantity: 110, unit: 'bags' or 'kg')
  raw_material     -> Other inputs bought
  medicine         -> Medicine/sprays/vaccines
  expense          -> Wages, electricity, repair
  purchase         -> Assets/equipment purchased
  unknown          -> greetings, status check-ins

JSON SCHEMA:
{
  "shead_name": "string (e.g. 'Shead 3', 'Chick Whites', 'Chick Brownie', none -> '')",
  "category": "string",
  "quantity": number,
  "unit": "string",
  "amount": number,
  "notes": "string",
  "confidence_score": number,
  "processed_text": "string"
}
Rules:
1. Multiple entries: If the message contains entries for multiple sheds or categories, output a JSON array of objects (one for each shed/entry).
2. Chick mortality: If the message lists separate mortality for Whites and Brownie (e.g. "Chick Whites: 2, Brownie: 1"), output two separate objects with shead_name as 'Chick Whites' and 'Chick Brownie' under category 'mortality'.
3. Identify shead name: 'shead3', 'S3' -> 'Shead 3'. Normalize spelling 'Shead' / 'Shed' to 'Shead' followed by number.
4. Only return valid JSON or JSON array. NO markdown blocks. NO other text."""


def _call_ollama(prompt: str, images: list = None, is_vision: bool = False, format_json: bool = True) -> any:
    url = f"{settings.OLLAMA_URL}/api/generate"
    model = settings.OLLAMA_VISION_MODEL if is_vision else settings.OLLAMA_MODEL
    
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    
    if format_json:
        payload["system"] = get_system_prompt("ollama")
        payload["format"] = "json"
    
    if images:
        payload["images"] = images
 
    try:
        response = requests.post(url, json=payload, timeout=600)
        response.raise_for_status()
        result = response.json()
        response_text = result.get("response", "")
        
        if not format_json:
            return response_text
            
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

def _call_gemini(prompt: str, images: list = None, document_path: str = None) -> dict:
    if not settings.GEMINI_API_KEY:
        print("Gemini API Key is not configured in environment variables.")
        return None
        
    try:
        model = genai.GenerativeModel(
            model_name="gemini-flash-latest",
            system_instruction=get_system_prompt("gemini"),
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
                    
        if document_path and document_path.endswith('.pdf'):
            try:
                with open(document_path, "rb") as f:
                    pdf_data = f.read()
                contents.append({
                    "mime_type": "application/pdf",
                    "data": pdf_data
                })
                print(f"Directly appended PDF document {document_path} to Gemini payload")
            except Exception as e:
                print(f"Failed to read PDF file for Gemini: {e}")
        
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

def _call_groq(prompt: str, images: list = None, is_vision: bool = False) -> dict:
    if not settings.GROQ_API_KEY:
        print("Groq API Key is not configured in environment variables.")
        return None
        
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Use vision model if images are provided or is_vision is true
    model = "llama-3.2-90b-vision-preview" if is_vision or images else "llama-3.1-8b-instant"
    
    messages = [
        {"role": "system", "content": get_system_prompt("gemini")} # We reuse Gemini's system prompt as it expects JSON natively without Ollama syntax issues
    ]
    
    user_content = []
    user_content.append({"type": "text", "text": prompt})
    
    if images:
        for img_b64 in images:
            user_content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{img_b64}"
                }
            })
            
    messages.append({"role": "user", "content": user_content})
    
    payload = {
        "model": model,
        "messages": messages,
        "response_format": {"type": "json_object"}
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        response_text = result["choices"][0]["message"]["content"]
        
        # Clean up markdown code blocks if any
        response_text = re.sub(r'```json\n?', '', response_text)
        response_text = re.sub(r'```\n?', '', response_text)
        
        return json.loads(response_text)
    except Exception as e:
        print(f"Groq API Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Groq response: {e.response.text}")
        return None

def _call_ai(prompt: str, images: list = None, is_vision: bool = False, document_path: str = None) -> dict:
    provider = settings.AI_PROVIDER.lower()
    if provider == "gemini":
        print("Using Gemini API for processing...")
        return _call_gemini(prompt, images, document_path)
    elif provider == "groq":
        print("Using Groq API for processing...")
        return _call_groq(prompt, images, is_vision)
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
        provider = settings.AI_PROVIDER.lower()
        if provider in ["gemini", "ollama"]:
            with open(image_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            
            prompt = "Extract farm data from this image. If there are calculations written in the image (like quantity * price), perform the math to find the total amount."
            if caption:
                prompt += f" The user also provided this caption: {caption}"
                
            if provider == "gemini":
                result = _call_gemini(prompt, images=[encoded_string])
            else:
                print(f"Using Ollama Vision model: {settings.OLLAMA_VISION_MODEL}")
                result = _call_ollama(prompt, images=[encoded_string], is_vision=True)
                
            if result:
                return result
        else:
            # Fallback to local OCR using Tesseract for providers without vision support (Groq/Ollama)
            print(f"Using Tesseract OCR for {provider} provider...")
            if pytesseract:
                try:
                    img = Image.open(image_path)
                    ocr_text = pytesseract.image_to_string(img)
                except Exception as e:
                    print(f"Tesseract OCR failed: {e}")
                    ocr_text = ""
            else:
                print("pytesseract is not installed or tesseract-ocr system package is missing.")
                ocr_text = ""
                
            if ocr_text.strip():
                print(f"OCR complete. Extracted text length: {len(ocr_text)}")
                # Now pass the extracted text transcription to the text model for structured parsing
                full_text = f"IMAGE OCR TRANSCRIPTION:\n{ocr_text}"
                if caption:
                    full_text += f"\n\nUSER CAPTION:\n{caption}"
                return process_text(full_text)
            elif caption.strip():
                print("OCR failed, but caption found. Processing caption text...")
                return process_text(caption)
            else:
                print("OCR failed to extract text from image.")
                
    except Exception as e:
        print(f"AI Image Pre-Processing Error: {e}")
        
    return _fallback_dummy_response(caption or "Image processing failed")

def process_document(doc_path: str, caption: str = "") -> dict:
    """Processes documents (PDFs) by passing directly to Gemini or extracting text locally for Ollama."""
    provider = settings.AI_PROVIDER.lower()
    if provider == "gemini":
        print("Processing PDF document directly with Gemini...")
        prompt = "Extract all relevant farm data records from this document."
        if caption:
            prompt += f" The user also provided this caption/note: {caption}"
        
        result = _call_ai(prompt, document_path=doc_path)
        if result:
            return result
        return _fallback_dummy_response(caption or "Gemini PDF processing failed")
        
    # Local text extraction fallback (for Ollama)
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
    """Fallback if AI provider fails or is unreachable."""
    return {
        "shead_name": "",
        "category": "unknown",
        "quantity": 0,
        "unit": "",
        "amount": 0.0,
        "notes": "AI processing failed or unreachable",
        "confidence_score": 0.0,
        "processed_text": text
    }
