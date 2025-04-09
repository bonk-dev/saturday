from dbContext import get_db
import sqlite3

def get_max_insertlog_id():
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("SELECT MAX(ID) FROM insertlog")
        max_id = cursor.fetchone()[0]
        if max_id is not None:
            return max_id
        else:
            return 0
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return 0

