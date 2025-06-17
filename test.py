import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load your API key from .env
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_AI_KEY"))

# Use the most stable latest Gemini model
model = genai.GenerativeModel("gemini-1.5-pro-latest")

# Generate response
response = model.generate_content("Summarize global migration patterns.")
print(response.text)
