import sqlite3

db_path = './tcc_backend.db'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

def show_table_data(table_name, limit=10):
    print(f"--- Dados da tabela {table_name} ---")
    cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit};")
    rows = cursor.fetchall()
    for row in rows:
        print(row)
    print("\n")

show_table_data("questions")
show_table_data("choices")

conn.close()