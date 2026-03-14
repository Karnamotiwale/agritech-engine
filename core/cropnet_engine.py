

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

    import json
    return json.dumps({
        "Disease Name": "Unknown (Rule-based Placeholder)",
        "Severity Level": "Medium",
        "Recommended Treatment": "Apply general fungicide if symptoms spread.",
        "Prevention Advice": "Maintain proper plant spacing and avoid over-watering."
    })
