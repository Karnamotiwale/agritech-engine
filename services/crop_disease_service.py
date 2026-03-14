import os
from dotenv import load_dotenv
from PIL import Image
from core.gemini_client import generate_ai_response

load_dotenv()


def analyze_crop_disease(image_path):

    img = Image.open(image_path)

    prompt = """
    Analyze this crop leaf image and determine:

    1. Disease name
    2. Severity level
    3. Treatment recommendation
    4. Prevention advice

    Explain clearly so farmers can understand.
    """

    response = generate_ai_response(prompt, image=img)

    return response