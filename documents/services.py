"""
📦 documents/services.py

This module contains all intelligence logic of the system.

🧠 RESPONSIBILITIES:
- OCR extraction
- Rule-based extraction
- AI-assisted extraction
- Document classification
- Variant detection
- Heuristic suggestions

🎯 DESIGN GOALS:
- Modular intelligence layers
- Safe AI integration
- Extensible for learning systems
"""

import re
import os
import json

import pytesseract
from PIL import Image

from openai import OpenAI

from .models import DocumentVariant, DocumentCategory


# =========================================================
# ⚙️ CONFIGURATION
# =========================================================
# Path to Tesseract OCR engine (Windows specific)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


# =========================================================
# 🤖 OPENAI CLIENT
# =========================================================
def get_openai_client():
    """
    Initializes OpenAI client using environment variable.

    Returns:
        OpenAI client or None if API key not set
    """
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("OpenAI key missing, skipping AI extraction")
        return None

    return OpenAI(api_key=api_key)


# =========================================================
# 🤖 AI EXTRACTION
# =========================================================
def ai_extract_fields(text):
    """
    Uses AI to extract structured data from OCR text.

    Returns:
        dict → parsed structured data
    """

    client = get_openai_client()

    if not client:
        return {}

    try:
        prompt = f"""
        Extract structured data from this document.

        Return ONLY valid JSON:
        {{
            "name": "",
            "dob": "",
            "document_type": "",
            "pan_number": "",
            "relationship": ""
        }}

        Text:
        {text}
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        content = response.choices[0].message.content

        # 🔥 IMPORTANT: convert string → dict
        return json.loads(content)

    except Exception as e:
        print("AI ERROR:", str(e))
        return {}


# =========================================================
# 🔀 VARIANT DETECTION
# =========================================================
def detect_variant(text, category):
    """
    Detects document variant (layout/version)

    Example:
        PAN_V1 vs PAN_QR vs PAN_NEW
    """

    variants = DocumentVariant.objects.filter(category__name=category)

    best_variant = None
    best_score = 0

    for variant in variants:
        score = 0

        for keyword in variant.keywords:
            if keyword.lower() in text.lower():
                score += 1

        if score > best_score:
            best_score = score
            best_variant = variant

    return best_variant, best_score


# =========================================================
# 🧠 CATEGORY CLASSIFICATION
# =========================================================
def classify_document(text):
    """
    Classifies document based on keyword matching.

    Returns:
        (category_name, confidence_score)
    """

    text = text.lower()
    categories = DocumentCategory.objects.all()

    best_match = None
    best_score = 0

    for category in categories:
        score = 0

        for keyword in category.keywords:
            if keyword.lower() in text:
                score += 1

        if score > best_score:
            best_score = score
            best_match = category

    if best_match:
        confidence = best_score / max(len(best_match.keywords), 1)
        return best_match.name, confidence

    return "Unknown", 0.0


# =========================================================
# 🧠 RULE-BASED DATA EXTRACTION
# =========================================================
def extract_structured_data(text):
    """
    Extracts structured fields using regex + heuristics.

    Current fields:
    - PAN number
    - DOB
    - Name

    Returns:
        dict
    """

    data = {}

    lines = [line.strip() for line in text.split("\n") if line.strip()]

    # ===============================
    # PAN NUMBER
    # ===============================
    pan_match = re.search(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b', text)
    if pan_match:
        data['pan_number'] = pan_match.group()

    # ===============================
    # DATE OF BIRTH
    # ===============================
    dob_match = re.search(r'\b\d{2}/\d{2}/\d{4}\b', text)
    if dob_match:
        data['dob'] = dob_match.group()

    # ===============================
    # NAME DETECTION (HEURISTIC)
    # ===============================
    for line in lines:
        clean_line = re.sub(r'[^A-Z ]', '', line.upper())

        if (
            len(clean_line.split()) >= 2 and
            len(clean_line) > 5 and
            "INCOME TAX" not in clean_line and
            "GOVT" not in clean_line and
            "PERMANENT" not in clean_line
        ):
            data['name'] = clean_line.strip()
            break

    return data


# =========================================================
# 🧠 HEURISTIC CATEGORY SUGGESTION
# =========================================================
def suggest_new_category(text):
    """
    Suggests new category when classification fails.

    Used as fallback before AI or admin creation.
    """

    text = text.lower()

    if "bank" in text and "statement" in text:
        return "Bank Statement"

    if "invoice" in text:
        return "Invoice"

    if "salary" in text or "payslip" in text:
        return "Salary Slip"

    return None


# =========================================================
# 🧠 OCR ENGINE
# =========================================================
def extract_text(file_path):
    """
    Extracts text from image using Tesseract OCR.

    Returns:
        string (cleaned text)
    """

    try:
        image = Image.open(file_path)

        text = pytesseract.image_to_string(image)

        print("OCR TEXT:", text)

        return text.strip()

    except Exception as e:
        print("OCR ERROR:", str(e))
        return ""