import requests
import sqlite3
import database

conn = database.get_db_connection()
doc = conn.execute("SELECT id FROM documents LIMIT 1").fetchone()
conn.close()

if doc:
    # Need to simulate a request or just call ai_service directly to test Q&A
    import ai_service
    # Mock chat history
    history = [{"role": "user", "message": "What is the document about?"}, {"role": "ai", "message": "It is a test document."}]
    try:
        ans = ai_service.answer_question("This is the raw content of the mock document.", history, "What did I just ask?")
        print("Answer:", ans)
    except Exception as e:
        import traceback
        traceback.print_exc()
else:
    print("No docs")
