from database.dbContext import get_db


def executeQuery(query: str, params: list = None):
    db = get_db()
    cursor = db.cursor()

    if params:
        cursor.execute(query, params)
    else:
       cursor.execute(query)

    return cursor.fetchall()



def getTableInfo(table_name: str):
    db = get_db()
    cursor = db.cursor()

    column_query = f"PRAGMA table_info({table_name})"
    cursor.execute(column_query)
    results = cursor.fetchall()

    column_info = []
    for row in results:
            column_info.append({
            'name': row[1],
            'type': row[2]
            })
    return column_info
