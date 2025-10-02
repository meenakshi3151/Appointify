import json
from google import genai
import dateparser
import os
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("API_KEY")
client = genai.Client(api_key=API_KEY)

def extract_entities_with_gemini(text):
    """
    Use Gemini to extract date, time, and department with confidence scores.
    """
    prompt = f"""
    Extract the following from the text:
    - date_phrase: natural language date expression
    - time_phrase: natural language time expression
    - department: medical department or type of doctor

    Include a confidence score (0 to 1) for each field.
    If any field is missing, set value to null and confidence to 0.

    Text: "{text}"

    Respond strictly in JSON format like this:
    {{
      "date_phrase": "<value or null>",
      "date_confidence": <0-1>,
      "time_phrase": "<value or null>",
      "time_confidence": <0-1>,
      "department": "<value or null>",
      "department_confidence": <0-1>
    }}
    """
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    result_text = response.candidates[0].content.parts[0].text.strip()
    if result_text.startswith("```"):
        result_text = result_text.strip("`")
        if result_text.lower().startswith("json"):
            result_text = result_text[len("json"):].strip()

    try:
        result = json.loads(result_text)
        return result
    except json.JSONDecodeError as e:
        print("JSON decode error:", e)
        print("Raw response:", result_text)
        return {
            "date_phrase": None,
            "date_confidence": 0.0,
            "time_phrase": None,
            "time_confidence": 0.0,
            "department": None,
            "department_confidence": 0.0
        }

def entity_recognition(content):
    gemini_result = extract_entities_with_gemini(content)
    confidences = [
        gemini_result.get("date_confidence", 0.0),
        gemini_result.get("time_confidence", 0.0),
        gemini_result.get("department_confidence", 0.0)
    ]
    entities_confidence = round(sum(confidences)/len(confidences), 2)
    result = {
        "entities": {
            "date_phrase": gemini_result.get("date_phrase"),
            "time_phrase": gemini_result.get("time_phrase"),
            "department": gemini_result.get("department")
        },
        "entities_confidence": entities_confidence
    }
    return json.dumps(result, indent=2)
