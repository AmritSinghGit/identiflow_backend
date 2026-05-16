import re,os
import pytesseract
from PIL import Image
from .models import DocumentVariant
from openai import OpenAI

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        return None

    return OpenAI(api_key=api_key)

def ai_extract_fields(text):
    client = get_openai_client()

    if not client:
        print("OpenAI key missing, skipping AI extraction")
        return {}

    try:
        prompt = f"""
        Extract structured data from this document.

        Return JSON with:
        - name
        - dob
        - document_type
        - id_number

        Text:
        {text}
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        return response.choices[0].message.content

    except Exception as e:
        print("AI ERROR:", str(e))
        return {}

def detect_variant(text, category):
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

def suggest_new_category(text):
    """
    AI-like heuristic suggestion for unknown documents
    """
    text = text.lower()

    if "bank" in text and "statement" in text:
        return "Bank Statement"

    if "invoice" in text:
        return "Invoice"

    if "salary" in text or "payslip" in text:
        return "Salary Slip"

    return None



def extract_text(file_path):
    try:
        image = Image.open(file_path)

        text = pytesseract.image_to_string(image)

        print("OCR TEXT:", text)  # DEBUG

        return text.strip()

    except Exception as e:
        print("OCR ERROR:", str(e))
        return ""


from .models import DocumentCategory


def classify_document(text):
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

def extract_structured_data(text):
    data = {}

    lines = [line.strip() for line in text.split("\n") if line.strip()]

    # PAN Number
    pan_match = re.search(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b', text)
    if pan_match:
        data['pan_number'] = pan_match.group()

    # DOB
    dob_match = re.search(r'\b\d{2}/\d{2}/\d{4}\b', text)
    if dob_match:
        data['dob'] = dob_match.group()

    # Name (improved logic)
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