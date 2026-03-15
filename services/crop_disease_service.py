from core.gemini_client import analyze_image  # type: ignore

def analyze_crop_disease(image_path):

    prompt = """
You are an expert agricultural plant pathologist.

Analyze the crop leaf image and determine the disease and recommended treatment.

Rules:
• Give short answers only.
• Maximum 2 sentences.
• Do NOT return JSON.
• Do NOT explain in detail.
• Use simple farmer-friendly language.
"""

    result = analyze_image(prompt, image_path)

    return result