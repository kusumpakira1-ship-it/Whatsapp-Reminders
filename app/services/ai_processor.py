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
        return r"""You are a specialized poultry farm data extraction AI. You read user messages and output a valid JSON object ONLY.
EXPECTED JSON SCHEMA:
{
  "shead_name": "string (e.g., 'Shead 3', multiple -> 'Shead 1, Shead 2')",
  "category": "string (exactly one of: 'egg_collection_1', 'egg_collection_2', 'egg_collection', 'hen_weight', 'mortality', 'egg_loaded', 'egg_unloaded', 'production', 'sales', 'feed', 'raw_material', 'medicine', 'expense', 'purchase', 'unknown')",
  "quantity": number (e.g. quantity of eggs, bags, kgs, hens),
  "unit": "string (e.g., 'trays', 'eggs', 'kg', 'bags')",
  "amount": number (monetary value, total price),
  "notes": "string (specific names, details, paid to/by for payments)",
  "confidence_score": number (0.0 to 1.0),
  "processed_text": "string (English translation)"
}
Rules:
1. Detect round: "1st", "morning", "subah" -> egg_collection_1. "2nd", "evening", "shaam" -> egg_collection_2. If round unclear -> egg_collection.
2. Hen weight: category -> hen_weight, quantity -> weight value, unit -> 'kg'.
3. Feed/Raw materials -> feed/raw_material. Medicine/vaccines -> medicine. Mortality -> mortality. Sales/becha -> sales.
4. If just greeting or shead number or "out" -> category: unknown.
5. WEIGHT SLIPS / GATE PASS / LOAD SLIPS: Extract RST No, Party Name, Material, Vehicle No, Bags, Gross Weight, Tare Weight, Net Weight, Date, Time each on its own line in 'notes'.
6. NO CODE BLOCKS, NO MARKDOWN. ONLY JSON."""

    return r"""
You are a specialized poultry farm data extraction AI.
Your job is to read WhatsApp messages from farm supervisors (in English, Hindi, Telugu, Tamil, Kannada, Malayalam, broken English, SMS shorthand) and extract farm records into a clean, structured JSON object.

=== CATEGORY CLASSIFICATION RULES ===
Use EXACTLY ONE of these category values:

  egg_collection_1 -> MORNING / 1st round egg collection. Keywords: 1st collection, first collection, morning collection, subah collection, batch 1, round 1, pratham, first round, morning batch
  egg_collection_2 -> EVENING / 2nd round egg collection. Keywords: 2nd collection, second collection, evening collection, shaam collection, batch 2, round 2, second round, evening batch
  egg_collection   -> General egg collection when round is NOT specified. Use only when 1st/2nd is genuinely unclear.
  hen_weight       -> Hen/bird body weight measurement. Keywords: weight, wt, kg weight, bird weight, hen weight, weighing, body weight
  mortality        -> Hen/bird deaths. Keywords: died, death, mort, dead, gir gayi, fell dead, hens died, chickens died
  egg_loaded       -> Eggs dispatched/sent out on trucks. Keywords: loaded, dispatch, sent, truck gaya, load out, bheja
  egg_unloaded     -> Eggs received/returned. Keywords: unloaded, returned, received back, wapas, received
  production       -> Flock stats: live bird count, batch age, total birds in shed
  sales            -> Egg sale revenue. Keywords: sold, sale, becha, rate, payment received for eggs
  feed             -> Feed/fodder given. Keywords: feed, dana, bags, feed consumed, mash, khana diya
  raw_material     -> Other farm inputs bought. Keywords: supplement, limestone, grit, material kharida
  medicine         -> Medicine/vaccines/treatments. Keywords: medicine, vaccine, spray, injection, tablet, viracid, tylosin, lasota, dawa
  expense          -> Farm operational costs. Keywords: labour, electricity, repair, transport, rent, wages, majdoori
  purchase         -> Equipment/asset purchases. Keywords: bought equipment, purchased, naya cage, tank
  egg              -> Legacy: general egg record when type genuinely unclear
  unknown          -> Cannot classify. Bare shead numbers, 'out', 'ok', single words, greetings.

=== EXTRACTION RULES ===
1. Translate everything into clean English.
2. Identify shead name: 'shead3', 'shed 3', 'S3', 'shead-3' -> 'Shead 3'. Multiple sheds -> comma separated. None -> empty string.
3. COLLECTION ROUND DETECTION (CRITICAL):
   - Words like '1st', 'first', 'morning', 'subah', 'pratham', 'AM', 'batch1', '1st round' -> egg_collection_1
   - Words like '2nd', 'second', 'evening', 'shaam', 'PM', 'batch2', '2nd round' -> egg_collection_2
   - If genuinely unclear which round -> egg_collection
4. HEN WEIGHT: Extract weight in kg. Put in quantity field with unit 'kg'. Put "Hen body weight: X kg" in notes.
5. Extract quantity as a number. SUM if multiple items. For eggs: use trays or pieces/eggs as unit.
6. Extract monetary amount as float. SUM all if multiple.
7. For multi-item messages: put breakdown in 'notes' with grand total at top, each item on its own line using escaped '\n'.
8. ONLINE PAYMENTS: Extract Paid By, Paid To, Bank, Transaction Ref, Date, Amount, Remarks each on its own line in 'notes'.
9. WEIGHT SLIPS / GATE PASS / LOAD SLIPS: Extract RST No, Party Name, Material, Vehicle No, Bags, Gross Weight, Tare Weight, Net Weight, Date, Time each on its own line in 'notes'.
10. confidence_score: 0.0 to 1.0
11. Single shead name alone, 'out', 'ok', greeting -> category: 'unknown', quantity: 0, amount: 0.0
12. YOU MUST ONLY RETURN VALID JSON. NO MARKDOWN. NO CODE BLOCKS. NO OTHER TEXT.

=== EXPECTED JSON SCHEMA ===
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

=== EXAMPLES ===
"Shead 3 morning collection 250 trays" -> {"shead_name":"Shead 3","category":"egg_collection_1","quantity":250,"unit":"trays","amount":0.0,"notes":"Morning (1st) collection","confidence_score":0.97,"processed_text":"Shead 3 - Morning 1st collection: 250 trays"}
"Shead 3 1st batch 180 eggs" -> {"shead_name":"Shead 3","category":"egg_collection_1","quantity":180,"unit":"eggs","amount":0.0,"notes":"1st round collection","confidence_score":0.96,"processed_text":"Shead 3 - 1st collection: 180 eggs"}
"Shead 5 evening 2nd collection 300 trays" -> {"shead_name":"Shead 5","category":"egg_collection_2","quantity":300,"unit":"trays","amount":0.0,"notes":"Evening (2nd) collection","confidence_score":0.97,"processed_text":"Shead 5 - Evening 2nd collection: 300 trays"}
"Shead 2 hen weight 1.8 kg" -> {"shead_name":"Shead 2","category":"hen_weight","quantity":1.8,"unit":"kg","amount":0.0,"notes":"Hen body weight: 1.8 kg","confidence_score":0.96,"processed_text":"Shead 2 - Hen weight: 1.8 kg"}
"Shead 2 5 hens died" -> {"shead_name":"Shead 2","category":"mortality","quantity":5,"unit":"hens","amount":0.0,"notes":"","confidence_score":0.95,"processed_text":"Shead 2 - 5 hens died"}
"Loaded 100 trays to truck" -> {"shead_name":"","category":"egg_loaded","quantity":100,"unit":"trays","amount":0.0,"notes":"","confidence_score":0.95,"processed_text":"Loaded 100 trays to truck"}
"sold 200 trays at 520 rupees" -> {"shead_name":"","category":"sales","quantity":200,"unit":"trays","amount":104000.0,"notes":"Grand Total Qty: 200 trays\nGrand Total Amt: 104000.00","confidence_score":0.97,"processed_text":"Sold 200 trays at Rs.520 each"}
"10 bags feed used shead1" -> {"shead_name":"Shead 1","category":"feed","quantity":10,"unit":"bags","amount":0.0,"notes":"","confidence_score":0.93,"processed_text":"Shead 1 - 10 bags of feed used"}
"Viracid 1kg spraying shead 8" -> {"shead_name":"Shead 8","category":"medicine","quantity":1,"unit":"kg","amount":0.0,"notes":"Activity: Viracid spraying","confidence_score":0.95,"processed_text":"Shead 8 - Viracid 1 kg spraying"}
"labour wages paid 3000" -> {"shead_name":"","category":"expense","quantity":0,"unit":"","amount":3000.0,"notes":"Labour wages paid","confidence_score":0.92,"processed_text":"Labour wages paid Rs.3000"}
"250 trays aaya" -> {"shead_name":"","category":"egg_collection","quantity":250,"unit":"trays","amount":0.0,"notes":"","confidence_score":0.95,"processed_text":"250 trays received"}
"Shead3" -> {"shead_name":"Shead 3","category":"unknown","quantity":0,"unit":"","amount":0.0,"notes":"","confidence_score":0.1,"processed_text":"Shead 3"}
"Shead 1 sold 100 trays at 520. Shead 2 sold 50 trays at 520." -> {"shead_name":"Shead 1, Shead 2","category":"sales","quantity":150,"unit":"trays","amount":78000.0,"notes":"Grand Total Qty: 150 trays\nGrand Total Amt: 78000.00\n--------------------\nShead 1: 100 trays at 520 (amount: 52000)\nShead 2: 50 trays at 520 (amount: 26000)","confidence_score":0.98,"processed_text":"Shead 1 sold 100 trays at 520. Shead 2 sold 50 trays at 520."}
"""

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
        response = requests.post(url, json=payload, timeout=300)
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
            model_name="gemini-pro",
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
    model = "llama-3.2-90b-vision-preview" if is_vision or images else "llama-3.3-70b-versatile"
    
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
        if provider == "gemini":
            with open(image_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            
            prompt = "Extract farm data from this image. If there are calculations written in the image (like quantity * price), perform the math to find the total amount."
            if caption:
                prompt += f" The user also provided this caption: {caption}"
                
            result = _call_gemini(prompt, images=[encoded_string])
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
