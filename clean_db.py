import sqlite3
import os

DB_PATH = 'app.db'

def list_documents():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    docs = conn.execute("SELECT id, filename, upload_date FROM documents").fetchall()
    conn.close()
    return docs

def delete_document(doc_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Delete related records first
    cursor.execute("DELETE FROM summaries WHERE doc_id = ?", (doc_id,))
    cursor.execute("DELETE FROM chats WHERE doc_id = ?", (doc_id,))
    cursor.execute("DELETE FROM mcqs WHERE doc_id = ?", (doc_id,))
    # Delete the document
    cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
    conn.commit()
    conn.close()
    print(f"\\n✅ Successfully deleted Document ID {doc_id} and all related data.")

if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        print("Database found not found. Please start the app first.")
        exit()

    docs = list_documents()
    if not docs:
        print("No documents found in the database. It is already clean!")
        exit()

    print("=== Your Uploaded Documents ===")
    for doc in docs:
        print(f"ID: {doc['id']} | Filename: {doc['filename']} | Date: {doc['upload_date']}")
    
    print("\\nWould you like to delete a document? (Enter ID number, or 'q' to quit)")
    choice = input("> ")

    if choice.isdigit():
        doc_id = int(choice)
        # Check if exists
        exists = any(d['id'] == doc_id for d in docs)
        if exists:
            delete_document(doc_id)
        else:
            print("Invalid Document ID.")
    else:
        print("Exiting...")
