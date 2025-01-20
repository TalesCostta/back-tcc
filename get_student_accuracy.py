import sqlite3

def get_student_accuracy(user_id):
    conn = sqlite3.connect('tcc_backend.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT COUNT(*) AS total_questions,
               SUM(CASE WHEN correct THEN 1 ELSE 0 END) AS correct_answers
        FROM student_progress
        WHERE user_id = ?
    ''', (user_id,))
    
    result = cursor.fetchone()
    total_questions = result[0]
    correct_answers = result[1] if result[1] is not None else 0
    
    if total_questions == 0:
        return 0  
    else:
        return (correct_answers / total_questions) * 10  