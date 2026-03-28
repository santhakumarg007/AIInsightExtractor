import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

chat_history = [{"role": "user", "message": "What is the document about?"}, {"role": "ai", "message": "It is a test document."}]
text = "This is the raw content."
new_question = "What did I just ask?"

system_instruction = (
    "You are a helpful AI assistant analyzing a document. "
    "Answer the user's question based strictly on the provided document.\n\n"
    f"Document Text:\n\"{text[:30000]}\""
)
model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=system_instruction)

formatted_history = []
for c in chat_history:
    role = "user" if c["role"] == "user" else "model"
    formatted_history.append({"role": role, "parts": [c["message"]]})
    
try:
    chat = model.start_chat(history=formatted_history)
    response = chat.send_message(new_question)
    print("SUCCESS")
    print(response.text)
except Exception as e:
    print("FAILED EXCEPTION:")
    print(repr(e))

