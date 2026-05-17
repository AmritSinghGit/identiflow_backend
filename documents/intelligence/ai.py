"""
📦 intelligence/ai.py

Handles OpenAI interaction.
"""

import os
from openai import OpenAI


def get_client():
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        return None

    return OpenAI(api_key=api_key)


def ai_extract_fields(text):
    client = get_client()

    if not client:
        print("AI SKIPPED (no key)")
        return {}

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": f"""
                    Extract:
                    - name
                    - dob
                    - id_number
                    - document_type

                    Text:
                    {text}
                    """
                }
            ],
            temperature=0
        )

        return response.choices[0].message.content

    except Exception as e:
        print("AI ERROR:", str(e))
        return {}