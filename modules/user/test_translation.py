import os
from google.cloud import translate_v2 as translate
from dotenv import load_dotenv

load_dotenv()

# Use raw string to handle backslashes properly
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"E:\Legal_Care\modules\user\legal-ai-translate-95e4aa01b1e8.json"


client = translate.Client()

# Language Detection Function
def detect_language(text: str) -> str:
    detection = client.detect_language(text)
    print(f"🔍 Detected Language: {detection['language']}")
    return detection['language']

# Translation Function
def translate_text(text: str, target_lang: str) -> str:
    result = client.translate(text, target_language=target_lang)
    print(f"🌐 Translated to ({target_lang}): {result['translatedText']}")
    return result['translatedText']

# Main Test
if __name__ == "__main__":
    english_text = "Justice delayed is justice denied."

    print(f"➡️ Original Text: {english_text}\n")

    # Detect the language
    detected_lang = detect_language(english_text)
    print()

    # Translate to Sinhala
    translate_text(english_text, "si")
    print()

    # Translate to Tamil
    translate_text(english_text, "ta")
    print()
