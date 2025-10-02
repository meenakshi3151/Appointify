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
    image_path = request.args.get('image_path') 
    if not image_path:
        return {"error": "Please provide an image_path parameter"}, 400
    ocr_result = text_extraction_from_noisy_image(image_path)
    return ocr_result

@app.route('/ner', methods=['GET', 'POST'])
def named_entity_recognition():
    raw_text = request.args.get('raw_text')
    if not raw_text:
        return {"error": "Please provide a raw_text parameter"}, 400
    ner_result = entity_recognition(raw_text)
    return ner_result

@app.route('/normalize', methods=['GET', 'POST'])
def normalize_entities():
    entities = request.args.get('entities')
    entities_confidence = request.args.get('entities_confidence')
    if not entities or not entities_confidence:
        return {"error": "Please provide entities and entities_confidence parameters"}, 400
    normalize_result = normalize_entities_with_gemini(entities, entities_confidence)
    return normalize_result

@app.route('/appointment', methods=['GET', 'POST'])
def schedule_of_appointment():
    normalized_entities = request.args.get('normalized_entities')
    normalized_entities_confidence = request.args.get('normalized_entities_confidence')
    if not normalized_entities or not normalized_entities_confidence:
        return {"error": "Please provide normalized and normalized_confidence parameters"}, 400
    appointment_result = send_appointment(json.loads(normalized_entities))
    return appointment_result

@app.route('/get_appointment', methods=['GET', 'POST'])
def get_appointment_from_image_or_text():
    image_path = request.args.get('image_path')
    input_text = request.args.get('input_text')
    timezone = request.args.get('timezone', 'Asia/Kolkata')
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
    appointment_result = send_appointment(normalize_result["normalized_entities"])
    return appointment_result

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
