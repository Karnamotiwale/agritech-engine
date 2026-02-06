import numpy as np
from PIL import Image
try:
    import tensorflow as tf
except ImportError:
    tf = None

MODEL_PATH = "models/cropnet/plant_disease_model.h5"

# Load model once
try:
    if tf:
        model = tf.keras.models.load_model(MODEL_PATH)
        print("CropNet Model Loaded Successfully")
    else:
        model = None
        print("TensorFlow not found. Mock mode active.")
except Exception as e:
    model = None
    print(f"Warning: Could not load CropNet model: {e}")

CLASS_NAMES = [
    "Healthy",
    "Bacterial Spot",
    "Early Blight",
    "Late Blight",
    "Leaf Mold"
]

def predict_crop_disease(image_path):
    if not model:
         # Fallback / Mock for when model isn't available
        return {
            "disease": "System Check Required",
            "confidence": 0.0,
            "error": "Model not loaded"
        }

    try:
        img = Image.open(image_path).resize((224, 224))
        img = np.array(img) / 255.0
        img = np.expand_dims(img, axis=0)

        preds = model.predict(img)[0]
        class_idx = np.argmax(preds)
        confidence = float(preds[class_idx])

        return {
            "disease": CLASS_NAMES[class_idx],
            "confidence": confidence
        }
    except Exception as e:
        return {
            "disease": "Error",
            "confidence": 0.0,
            "error": str(e)
        }
