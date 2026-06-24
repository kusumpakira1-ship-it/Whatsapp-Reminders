import json
import google.generativeai as genai
from core.config import settings
import typing_extensions as typing

# Initialize Gemini
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)

# Define the expected structured output schema using standard Python typing
class FarmExtraction(typing.TypedDict):
    farm_name: str
    category: str  # egg, feed, medicine, mortality, sales, purchase, expense, unknown
    quantity: float
    unit: str
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
6. Store the translated, clean English version in 'processed_text'.
7. Estimate your confidence (0.0 to 1.0).

EXAMPLES:
"250 ట్రేలు వచ్చాయి" -> {"farm_name":"", "category":"egg", "quantity":250, "unit":"trays", "notes":"", "confidence_score": 0.95, "processed_text": "250 trays received"}
"frm3 200 trys tdy" -> {"farm_name":"Farm 3", "category":"egg", "quantity":200, "unit":"trays", "notes":"today", "confidence_score": 0.9, "processed_text": "Farm 3 collected 200 trays today"}
"""

def process_text(text: str) -> dict:
    """Processes plain text using Gemini."""
    if not settings.GEMINI_API_KEY:
        return _fallback_dummy_response(text)
        
    model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=get_system_prompt())
    try:
        response = model.generate_content(
            f"Extract data from this message:\n{text}",
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
            )
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"AI Text Processing Error: {e}")
        return _fallback_dummy_response(text)

def process_image(image_path: str, caption: str = "") -> dict:
    """Processes images (OCR + Understanding) using Gemini."""
    if not settings.GEMINI_API_KEY:
        return _fallback_dummy_response(caption or "Image file")
        
    try:
        import PIL.Image
        img = PIL.Image.open(image_path)
        model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=get_system_prompt())
        
        prompt = "Extract farm data from this image."
        if caption:
            prompt += f" The user also provided this caption: {caption}"
            
        response = model.generate_content(
            [prompt, img],
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
            )
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"AI Image Processing Error: {e}")
        return _fallback_dummy_response(caption or "Image processing failed")

def process_document(doc_path: str, caption: str = "") -> dict:
    """Processes documents (PDFs) using Gemini File API."""
    if not settings.GEMINI_API_KEY:
        return _fallback_dummy_response(caption or "Document file")
        
    try:
        # Upload file to Gemini
        uploaded_file = genai.upload_file(path=doc_path)
        model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=get_system_prompt())
        
        prompt = "Extract the relevant farm data summary from this document."
        if caption:
            prompt += f" User caption: {caption}"
            
        response = model.generate_content(
            [uploaded_file, prompt],
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
            )
        )
        
        # Cleanup file from Gemini servers
        genai.delete_file(uploaded_file.name)
        
        return json.loads(response.text)
    except Exception as e:
        print(f"AI Document Processing Error: {e}")
        return _fallback_dummy_response(caption or "Document processing failed")

def _fallback_dummy_response(text: str) -> dict:
    """Fallback if Gemini fails or is not configured."""
    return {
        "farm_name": "",
        "category": "unknown",
        "quantity": 0,
        "unit": "",
        "notes": "AI processing failed or API key missing",
        "confidence_score": 0.0,
        "processed_text": text
    }
