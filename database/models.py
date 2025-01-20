import sqlite3
from database.setup import create_connection

def insert_user(username, email, password, role):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)",
                   (username, email, password, role))

    conn.commit()
    conn.close()

def get_user_by_email(email):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, email, password, role FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "id": row[0],
            "username": row[1],
            "email": row[2],
            "password": row[3],
            "role": row[4],
        }
    return None

def insert_question(question_text, difficulty):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO questions (question_text, difficulty) VALUES (?, ?)",
                   (question_text, difficulty))

    conn.commit()
    conn.close()

def get_questions_by_difficulty(difficulty):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM questions WHERE difficulty = ?", (difficulty,))
    questions = cursor.fetchall()

    conn.close()
    return questions
    