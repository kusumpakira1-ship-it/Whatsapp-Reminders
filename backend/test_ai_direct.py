import sys
import os

# Add parent dir to path so we can import from ai_processor
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_processor import process_text

test_message = "Shead 3: Egg collection morning round 12 trays"
print(f"Testing message: {repr(test_message)}")
result = process_text(test_message)
print("Result:")
import json
print(json.dumps(result, indent=2))
