from dotenv import load_dotenv
import os
from google.cloud import translate_v2 as translate

# Load environment variables
load_dotenv()

# Set the credentials path explicitly
google_credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "E:\\Legal_Care\\modules\\user\\legal-ai-translate-95e4aa01b1e8.json")
if not google_credentials:
    raise ValueError("❌ GOOGLE_APPLICATION_CREDENTIALS is not set in the .env file or default path.")

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = google_credentials

# Initialize Google Translate client
client = translate.Client()

# Language detection function
def detect_language(text: str) -> str:
    result = client.detect_language(text)
    return result["language"]

# Translate to English
def translate_to_english(text: str) -> str:
    return client.translate(text, target_language="en")["translatedText"]

# Translate from English to another language
def translate_from_english(text: str, target_lang: str) -> str:
    return client.translate(text, target_language=target_lang)["translatedText"]
