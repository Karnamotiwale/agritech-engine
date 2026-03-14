import os
from google import genai
from dotenv import load_dotenv
from PIL import Image

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


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

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[prompt, img]
    )

    return response.text