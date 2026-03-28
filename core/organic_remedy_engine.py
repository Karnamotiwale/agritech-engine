# core/organic_remedy_engine.py

def generate_organic_remedy(crop: str, disease: str) -> dict:
    """
    Generalized disease-to-organic-remedy engine analyzing 38+ plantvillage classes.
    Categorizes based on pathogen/pest signatures.
    """
    disease_lower = disease.lower() if disease else ""
    
    # Healthy Baseline
    if "healthy" in disease_lower:
        return {
            "organic_remedies": [
                "No active treatment required. Crop is healthy.",
                "Continue standard fertilization cycle",
                "Apply preemptive compost tea bi-weekly"
            ],
            "prevention": [
                "Maintain optimal soil moisture",
                "Practice regular crop rotation",
                "Ensure good airflow between plants"
            ]
        }
        
    # Signatures
    is_fungal = any(k in disease_lower for k in ["blight", "rust", "mildew", "spot", "rot", "smut", "scab", "fungus"])
    is_bacterial = any(k in disease_lower for k in ["bacterial", "fire blight", "canker"])
    is_pest = any(k in disease_lower for k in ["mite", "aphid", "beetle", "worm", "hopper", "bug", "weevil", "miner"])
    is_viral = any(k in disease_lower for k in ["virus", "mosaic", "curl", "yellows", "streak"])
    
    remedies = []
    prevention = []
    
    if is_fungal:
        remedies.extend([
            "Spray neem oil every 5–7 days directly onto affected leaves",
            "Apply a diluted baking soda (sodium bicarbonate) spray weekly",
            "Use compost tea foliar spray to boost beneficial microbes on leaves"
        ])
        prevention.extend([
            "Avoid overhead watering; use drip irrigation to keep foliage dry",
            "Remove and destroy heavily blighted or infected leaves immediately",
            "Improve air circulation through optimal plant spacing and pruning"
        ])
        
    elif is_bacterial:
        remedies.extend([
            "Apply organic copper soap fungicide immediately",
            "Prune out infected branches/leaves at least 12 inches below visible symptoms",
            "Apply neem oil as a broad-spectrum deterrent alongside copper"
        ])
        prevention.extend([
            "Sanitize all pruning tools strictly between cuts with isopropyl alcohol",
            "Do not work closely with plants while foliage is wet",
            "Employ a 3-year crop rotation strictly avoiding the same family"
        ])
        
    elif is_pest:
        remedies.extend([
            "Spray neem oil every 3–5 days paying attention to the underside of leaves",
            "Use garlic or hot pepper extract spray directly onto colonies",
            "Introduce beneficial insects (e.g., ladybugs or lacewings)"
        ])
        prevention.extend([
            "Plant trap crops to lure pests away from primary harvest",
            "Utilize reflective mulches to disorient flying insects",
            "Avoid high-nitrogen fertilizers which attract aphid outbreaks"
        ])
        
    elif is_viral:
        remedies.extend([
            "There are no organic 'cures' for plant viruses. Immediate action required.",
            "Physically remove and burn the infected plant to protect the rest of the crop",
            "Vigorously control vector pests (aphids/thrips) with neem or garlic spray"
        ])
        prevention.extend([
            "Use certified virus-free seeds and resistant cultivars",
            "Vigilantly manage weeds, which often harbor viral reservoirs",
            "Do not smoke tobacco near plants to avoid Tobacco Mosaic Virus transmission"
        ])
        
    else:
        # Fallback Unknown Pathegon
        remedies.extend([
            "Isolate the plant if possible while monitoring symptoms closely",
            "Apply a mild neem oil spray as a preventative broad-spectrum defense",
            "Ensure the plant is not suffering from nutrient deficiency or water stress"
        ])
        prevention.extend([
            "Avoid excessive moisture and overhead watering",
            "Provide balanced compost-based nutrition",
            "Keep the farm rigorously free of decaying plant matter"
        ])
        
    return {
        "organic_remedies": remedies,
        "prevention": prevention
    }
