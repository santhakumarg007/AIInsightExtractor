import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

prompt = "Hello"
try:
    model = genai.GenerativeModel('gemini-flash-latest')
    response = model.generate_content(prompt)
    print("Success:")
    print(response.text)
except Exception as e:
    import traceback
    traceback.print_exc()
