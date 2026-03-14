from core.gemini_client import analyze_image

def analyze_crop_disease(image_path):

    prompt = """
You are an expert agricultural plant pathologist.

Analyze the crop leaf image and determine:

1. Possible disease
2. Symptoms observed
3. Recommended treatment
4. Prevention advice

Respond in JSON format:
{
 "disease": "",
 "symptoms": "",
 "treatment": "",
 "prevention": ""
}
"""

    result = analyze_image(prompt, image_path)

    return result