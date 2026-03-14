from core.gemini_service import ask_gemini

def predict_crop_disease(image_description):

    prompt = f"""
A farmer uploaded a crop image.

Analyze the crop disease and return:

1. Disease Name
2. Severity Level (Low / Medium / High)
3. Recommended Treatment
4. Prevention Advice

Image description:
{image_description}
"""

    response = ask_gemini(prompt)

    return response
