from PIL import Image, ImageFilter, ImageEnhance
import pytesseract
import json

def text_extraction_from_noisy_image(image_path):
    # Preprocess the image for better OCR results as mentioned in the Step 1 to reduce noise
    img = Image.open(image_path)
    img = img.convert('L') 
    img = img.filter(ImageFilter.MedianFilter())
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2)  
    # Perform OCR using pytesseract
    text = pytesseract.image_to_string(img).strip()
    ocr_data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
    confidences = [int(c) for c in ocr_data['conf'] if int(c) >= 0]
    average_conf = sum(confidences) / len(confidences) if confidences else 0
    result = {
        "raw_text": text,
        "confidence": round(average_conf / 100, 2) 
    }
    return json.dumps(result, indent=2)
