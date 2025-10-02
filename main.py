from flask import Flask 
from utils.ocr import text_extraction_from_noisy_image
from utils.ner import entity_recognition
from utils.normalize import normalize_entities_with_gemini
from utils.appointment import send_appointment
from flask import request
import json

# Initialize the Flask application
app = Flask(__name__)

# Define a route for the root URL
@app.route('/')
def appointfy():
    return "Welcome to Appointfy!"

@app.route('/ocr', methods=['GET', 'POST'])
def optimal_character_recognition():
    data = request.get_json()
    image_path = data.get('image_path') if data else None
    if not image_path:
        return {"error": "Please provide an image_path parameter"}, 400
    ocr_result = text_extraction_from_noisy_image(image_path)
    return ocr_result

@app.route('/ner', methods=['GET'])
def named_entity_recognition():
    raw_text = request.get_json().get('raw_text') if request.is_json else None
    if not raw_text:
        return {"error": "Please provide a raw_text parameter"}, 400
    content = {
        "raw_text": raw_text
    }
    ner_result = entity_recognition(content)
    return ner_result

@app.route('/normalize', methods=['GET'])
def normalize_entities():
    entities = request.get_json().get('entities') if request.is_json else None
    entities_confidence = request.get_json().get('entities_confidence') if request.is_json else None
    if not entities or not entities_confidence:
        return {"error": "Please provide entities and entities_confidence parameters"}, 400
    normalize_result = normalize_entities_with_gemini(entities, entities_confidence)
    return normalize_result

@app.route('/appointment', methods=['GET'])
def schedule_of_appointment():
    normalized_entities = request.get_json().get('normalized') if request.is_json else None
    normalized_entities_confidence = request.get_json().get('normalized_confidence') if request.is_json else None
    if not normalized_entities or not normalized_entities_confidence:
        return {"error": "Please provide normalized and normalized_confidence parameters"}, 400
    appointment_result = send_appointment({
        "normalized": normalized_entities,
        "normalized_confidence": normalized_entities_confidence
    })
    return appointment_result

@app.route('/get_appointment', methods=['POST'])
def get_appointment_from_image_or_text():
    data = request.get_json() if request.is_json else {}
    image_path = data.get('image_path')
    input_text = data.get('input_text')
    timezone = data.get('timezone', "Asia/Kolkata")
    if not image_path and not input_text:
        return {"error": "Please provide either an image_path or input_text parameter"}, 400
    if image_path:
        ocr_result = text_extraction_from_noisy_image(image_path)   
    else:
        ocr_result = json.dumps({"raw_text": input_text, "confidence": 1.0})
    entities_recognition_result = json.loads(entity_recognition(json.loads(ocr_result)))
    entities = entities_recognition_result['entities']
    entities_confidence = entities_recognition_result['entities_confidence']
    normalize_result = normalize_entities_with_gemini(entities, entities_confidence, tz=timezone)
    if normalize_result.get("status") == "needs_clarification":
        return normalize_result
    appointment_result = send_appointment(normalize_result)
    return appointment_result

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
