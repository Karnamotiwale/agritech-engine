from core.gemini_client import analyze_image  # type: ignore

def analyze_crop_disease(image_path):

    prompt = """
You are an expert agricultural plant pathologist.

Analyze the crop leaf image and determine the disease and recommended treatment.

Rules:
• You must return ONLY a strictly formatted JSON object with no markdown formatting.
• The payload must exactly match this format:
{"crop": "Identified Crop Name", "disease": "Identified Disease Name or Healthy", "confidence": 95.5}
"""

    result = analyze_image(prompt, image_path)

    return result