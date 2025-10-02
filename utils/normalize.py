import json
from datetime import datetime
from google import genai
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("API_KEY")
client = genai.Client(api_key=API_KEY)

def normalize_entities_with_gemini(entities, entities_confidence, tz="Asia/Kolkata"):
    """
    Normalize date, time, and department using Gemini only if entities_confidence is 1.0.
    Otherwise, return guardrail JSON for ambiguous input.
    """
    threshold = 0.7
    if entities_confidence < threshold:
        return {"status":"needs_clarification",
                "message":"Ambiguous date/time or department"}
    now = datetime.now()
    current_date = now.strftime("%Y-%m-%d")
    current_time = now.strftime("%H:%M")
    prompt = f"""
    You are a medical appointment entity extractor.
    Current date: {current_date}
    Current time: {current_time}
    Timezone: {tz}
    Return **a confidence score (0-1) for each entity**.  
    If you cannot confidently determine a value, set confidence < {threshold}.
    From the following text, extract and normalize the following entities:
       - "date_phrase": The date expression in the text (e.g., "next Friday", "Oct 10"). If it is a relative date like "next Friday", resolve it into the exact calendar date based on {current_date} and return it in YYYY-MM-DD format.
       - "time_phrase": The time mentioned (e.g., "3pm", "14:30"). Convert it into 24-hour format (HH:MM) if present.
       - "department" : Identify the medical department.  
            - If the text explicitly mentions a department (e.g., cardiology, dentistry), return it.  
            - If the text uses indirect wording (like symptoms, problems, or layman terms), interpret it and map it to the most suitable *general medical department*.  
            - Use broad, standardized categories of doctors such as (but not limited to):  
                - General physician  
                - Dentist  
                - Cardiologist  
                - Dermatologist  
                - Neurologist  
                - Orthopedist  
                - Ophthalmologist  
                - Psychiatrist  
                - Gynecologist  
                - Pediatrician  
            - If no department can be matched, return null.

    Text: "{entities}"
    Respond strictly in JSON format only (no markdown, no extra text), exactly like this structure:
   {{
      "normalized": {{
        "date": "<YYYY-MM-DD or null>",
        "time": "<HH:MM or null>",
        "department": "<department or null>",
        "tz": "{tz}"
      }},
      "date_confidence": <0-1>,
      "time_confidence": <0-1>,
      "department_confidence": <0-1>
    }}
    """
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    result_text = response.candidates[0].content.parts[0].text.strip()
    if result_text.startswith("```"):
        result_text = result_text.strip("`")
        if result_text.lower().startswith("json"):
            result_text = result_text[len("json"):].strip()

    try:
        result = json.loads(result_text)
        if (result.get("date_confidence", 0.0) < threshold or
            result.get("time_confidence", 0.0) < threshold or
            result.get("department_confidence", 0.0) < threshold):
            return {"status":"needs_clarification",
                    "message":"Ambiguous date/time or department"}

        return {
            "normalized_entities": result.get("normalized"),
            "normalized_entities_confidence": round(
                (result["date_confidence"] + result["time_confidence"] + result["department_confidence"])/3, 2
            )
        }
    except json.JSONDecodeError:
        return {"status":"needs_clarification",
                "message":"Failed to parse normalized output"}
