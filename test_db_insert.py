import sqlite3
import database
import ai_service

conn = database.get_db_connection()
doc = conn.execute("SELECT id, content FROM documents LIMIT 1").fetchone()
if not doc:
    print("No documents found in DB.")
    conn.close()
    exit()

doc_id = doc["id"]
content = doc["content"]
print(f"Testing with doc_id={doc_id}")

try:
    result = ai_service.get_summary_and_insights(content, "medium")
    print("Result type:", type(result))
    print("Result:", result)
    
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO summaries (doc_id, size, summary_text, context, methodology, key_features, advantages, disadvantages)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (doc_id, "medium", result.get("summary", ""), result.get("context", ""), 
          result.get("methodology", ""), result.get("key_features", ""),
          result.get("advantages", ""), result.get("disadvantages", "")))
    conn.commit()
    print("Insert successful!")
except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"DB Error: {e}")
finally:
    conn.close()
