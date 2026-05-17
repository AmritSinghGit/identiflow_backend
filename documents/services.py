"""
📦 documents/services.py

🧠 CORE INTELLIGENCE LAYER

Handles:
✔ OCR extraction
✔ Rule-based extraction
✔ AI extraction (multi-provider ready)
✔ Classification
✔ Variant detection

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚨 RULES:
✔ NEVER trust external data (OCR / AI)
✔ ALWAYS return safe defaults
✔ AI must NEVER break pipeline
"""

import re
import os
import json
from .logger import log_event

import pytesseract
from PIL import Image
from openai import OpenAI

from .models import DocumentVariant, DocumentCategory


# =========================================================
# ⚙️ CONFIGURATION
# =========================================================
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


# =========================================================
# 🤖 OPENAI CLIENT
# =========================================================
def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        log_event("AI_SKIPPED_NO_KEY")
        return None

    return OpenAI(api_key=api_key)


# =========================================================
# 🤖 AI EXTRACTION (MULTI-PROVIDER READY)
# =========================================================
def ai_extract_fields(text, provider="openai"):
    """
    Extract structured data using AI.

    ALWAYS returns dict (safe)
    """

    if not text:
        return {}

    try:
        if provider == "openai":
            return _openai_extract(text)

        # Future:
        # if provider == "claude":
        #     return _claude_extract(text)

        return {}

    except Exception as e:
        log_event("AI_ERROR", {"error": str(e)}, level="error")
        return {}


def _openai_extract(text):
    """
    OpenAI extraction logic
    """

    client = get_openai_client()

    if not client:
        return {}

    prompt = f"""
    Extract structured data from this document.

    Return ONLY valid JSON:
    {{
        "name": "",
        "dob": "",
        "pan_number": "",
        "document_type": "",
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

    # =========================================================
    # 🛡️ SAFE JSON PARSING
    # =========================================================
    try:
        # remove markdown if present
        content = content.strip()
        if content.startswith("```"):
            content = content.split("```")[1]

        return json.loads(content)

    except Exception:
        log_event("AI_PARSE_FAILED", {"raw": content[:200]}, level="error")
        return {}


# =========================================================
# 🔀 VARIANT DETECTION
# =========================================================
def detect_variant(text, category):
    text = text or ""

    variants = DocumentVariant.objects.filter(category__name=category)

    best_variant = None
    best_score = 0

    for variant in variants:
        score = 0

        for keyword in (variant.keywords or []):
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
    text = (text or "").lower()

    log_event("CLASSIFY_START", {"text_preview": text[:50]})

    categories = DocumentCategory.objects.all()

    best_match = None
    best_score = 0

    for category in categories:
        score = 0

        for keyword in (category.keywords or []):
            if keyword.lower() in text:
                score += 1

        if score > best_score:
            best_score = score
            best_match = category

    if best_match:
        confidence = best_score / max(len(best_match.keywords), 1)

        log_event("CLASSIFY_RESULT", {
            "category": best_match.name,
            "confidence": confidence
        })

        return best_match.name, confidence

    log_event("CLASSIFY_RESULT", {"category": "Unknown"})
    return "Unknown", 0.0


# =========================================================
# 🧠 RULE-BASED EXTRACTION
# =========================================================
def extract_structured_data(text):
    data = {}

    if not text:
        return {}

    lines = [line.strip() for line in text.split("\n") if line.strip()]

    # PAN
    pan_match = re.search(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b', text)
    if pan_match:
        data['pan_number'] = pan_match.group()

    # DOB
    dob_match = re.search(r'\b\d{2}/\d{2}/\d{4}\b', text)
    if dob_match:
        data['dob'] = dob_match.group()

    # NAME
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
    text = (text or "").lower()

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
    try:
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image) or ""

        log_event("OCR_COMPLETED", {"length": len(text)})

        return text.strip()

    except Exception as e:
        log_event("OCR_ERROR", {"error": str(e)}, level="error")
        return ""