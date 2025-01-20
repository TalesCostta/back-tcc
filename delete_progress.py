import sqlite3

def create_connection():
    conn = None
    try:
        conn = sqlite3.connect('tcc_backend.db')
    except sqlite3.Error as e:
        print(e)
    return conn

def delete_student_progress(user_id):
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()

            cursor.execute('DELETE FROM student_progress WHERE user_id = ?', (user_id,))
            conn.commit()

            print(f"Progresso do estudante com ID {user_id} foi apagado com sucesso!")
        except sqlite3.Error as e:
            print(f"Erro ao apagar progresso: {e}")
        finally:
            conn.close()
    else:
        print("Erro ao conectar ao banco de dados.")

if __name__ == "__main__":
    delete_student_progress(1)