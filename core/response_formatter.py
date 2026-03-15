def short_response(text: str) -> str:
    """
    Ensure the text is at most 2-3 sentences long and farmer-friendly.
    """
    if not text:
        return ""
    
    # Simple sentence splitting on punctuation
    import re
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    
    # Take the first 2 sentences. If they are very short, maybe 3.
    # But as per requirements, "max 2-3 sentences", we'll just take 2 to be safe and concise.
    # type: ignore
    short = " ".join(sentences[:2])
    return short.strip()
