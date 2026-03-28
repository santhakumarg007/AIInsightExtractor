import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

def configure_gemini():
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)

def get_summary_and_insights(text, size):
    """
    Returns a comprehensive summary and insights as a dictionary based on the provided text.
    size: 'small', 'medium', or 'large'
    """
    configure_gemini()
    
    size_instruction = {
        'small': 'very concise, around 1-2 paragraphs',
        'medium': 'detailed, around 3-4 paragraphs',
        'large': 'comprehensive, long and highly detailed'
    }

    instruction = size_instruction.get(size, 'detailed')

    prompt = f"""
    Analyze the following document text and provide:
    1. A short summary ({instruction}).
    2. Context of the document.
    3. Methodology (if applicable, otherwise 'N/A').
    4. Key features.
    5. Advantages.
    6. Disadvantages.

    Format the response STRICTLY as a JSON object with these exact keys:
    "summary", "context", "methodology", "key_features", "advantages", "disadvantages"

    Document text:
    "{text[:30000]}" # Limiting text to avoid token limits for now
    """

    try:
        model = genai.GenerativeModel('gemini-flash-latest')
        response = model.generate_content(prompt)
        # Parse the JSON from the markdown block or raw text
        raw_text = response.text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:-3]
        elif raw_text.startswith("```"):
            raw_text = raw_text[3:-3]
            
        return json.loads(raw_text)
    except Exception as e:
        print(f"Error in Gemini summarize: {e}")
        return {
            "summary": "Error analyzing document.",
            "context": "N/A", "methodology": "N/A", "key_features": "N/A", 
            "advantages": "N/A", "disadvantages": "N/A"
        }

def answer_question(text, chat_history, new_question):
    """
    Answers a question based on document text and previous chat history.
    """
    configure_gemini()
    
    try:
        model = genai.GenerativeModel('gemini-flash-latest')

        formatted_history = []
        for c in chat_history:
            role = "user" if c["role"] == "user" else "model"
            if formatted_history and formatted_history[-1]["role"] == role:
                formatted_history[-1]["parts"][0] += "\n\n" + c["message"]
            else:
                formatted_history.append({"role": role, "parts": [c["message"]]})
                
        if formatted_history and formatted_history[0]["role"] == "model":
            formatted_history.pop(0)
            
        instruction = (
            "You are a helpful AI assistant analyzing a document. "
            "Answer the user's question based strictly on the provided document.\n\n"
            f"Document Text:\n\"{text[:30000]}\"\n\n"
        )
        
        if formatted_history:
            formatted_history[0]["parts"][0] = instruction + formatted_history[0]["parts"][0]
        else:
            new_question = instruction + new_question
            
        chat = model.start_chat(history=formatted_history)
        response = chat.send_message(new_question)
        return response.text.strip()
    except Exception as e:
        print(f"Error in Gemini chat: {e}")
        return f"Sorry, I could not answer that due to an internal error: {e}"

def generate_mcqs(text):
    """
    Generates 5 multiple choice questions based on the text.
    Returns a list of dictionaries with keys: question, options (list of 4 strings), answer (index 0-3)
    """
    configure_gemini()
    prompt = f"""
    Generate exactly 5 multiple choice questions based on the following text to test the user's comprehension.
    Each question should have 4 options and 1 correct answer.
    
    Format EXACTLY as a JSON array of objects with keys: "question", "options" (array of 4 text options), "answer" (0-based index of correct option).

    Text:
    "{text[:30000]}"
    """
    try:
        model = genai.GenerativeModel('gemini-flash-latest')
        response = model.generate_content(prompt)
        raw_text = response.text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:-3]
        elif raw_text.startswith("```"):
            raw_text = raw_text[3:-3]
        return json.loads(raw_text)
    except Exception as e:
        print(f"Error in Gemini MCQ generator: {e}")
        return []

def tret_ai_general_chat(chat_history, new_question):
    """
    Answers general questions natively using GenAI acting as Tret AI, the site assistant.
    Does not depend on a specific document context.
    """
    configure_gemini()
    try:
        model = genai.GenerativeModel('gemini-flash-latest')
        
        formatted_history = []
        for c in chat_history:
            role = "user" if c["role"] == "user" else "model"
            if formatted_history and formatted_history[-1]["role"] == role:
                formatted_history[-1]["parts"][0] += "\n\n" + c["message"]
            else:
                formatted_history.append({"role": role, "parts": [c["message"]]})
                
        if formatted_history and formatted_history[0]["role"] == "model":
            formatted_history.pop(0)

        instruction = (
            "You are Tret AI, a highly intelligent, friendly, and helpful GenAI and RAG-based assistant. "
            "Your main role is to help users navigate and use 'Insight Extractor', a web app that processes PDFs, DOCX, and TXT files, summarizes them, answers questions about them via RAG chat, generates MCQs for quiz learning, and saves history. "
            "Always be welcoming, friendly, and use simple language. "
            "You can answer general questions, but if they ask about a specific document, tell them to upload it and use the Document Analysis tab.\n\n"
        )
        
        if formatted_history:
            formatted_history[0]["parts"][0] = instruction + formatted_history[0]["parts"][0]
        else:
            new_question = instruction + new_question
            
        chat = model.start_chat(history=formatted_history)
        response = chat.send_message(new_question)
        return response.text.strip()
    except Exception as e:
        print(f"Error in Tret AI chat: {e}")
        return "Sorry, I am having trouble connecting to my servers right now."

def generate_flashcards(text):
    """
    Generates 10 flashcards from the text format {"front": "", "back": ""}.
    """
    configure_gemini()
    prompt = f"""
    Generate exactly 10 high-quality study flashcards based on the following text.
    Format EXACTLY as a JSON array of objects with keys: "front" (the question or concept), "back" (the concise answer or definition).
    Text: "{text[:30000]}"
    """
    try:
        model = genai.GenerativeModel('gemini-flash-latest')
        response = model.generate_content(prompt)
        raw_text = response.text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:-3]
        elif raw_text.startswith("```"):
            raw_text = raw_text[3:-3]
        return json.loads(raw_text)
    except Exception as e:
        print(f"Error generating flashcards: {e}")
        return []

def compare_documents(texts):
    """ 
    Compares an array of text contents and returns a structured JSON evaluation. 
    """
    configure_gemini()
    docs_text = ""
    for idx, t in enumerate(texts):
        docs_text += f"\\n\\n--- Document {idx+1} ---\\n{t[:15000]}"
        
    prompt = f"""
    You are an expert analyst. Compare and contrast the following documents.
    Provide your analysis STRICTLY as a JSON object with these exact keys:
    "common_themes" (array of strings),
    "contrasting_points" (array of strings),
    "holistic_summary" (a detailed paragraph),
    "combined_advantages" (array of strings)

    Documents:
    {docs_text}
    """
    try:
        model = genai.GenerativeModel('gemini-flash-latest')
        response = model.generate_content(prompt)
        raw_text = response.text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:-3]
        elif raw_text.startswith("```"):
            raw_text = raw_text[3:-3]
        return json.loads(raw_text)
    except Exception as e:
        print(f"Error in document comparison: {e}")
        return {
            "common_themes": [],
            "contrasting_points": [],
            "holistic_summary": "Failed to compare.",
            "combined_advantages": []
        }
