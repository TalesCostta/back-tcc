import sqlite3
from flask import Flask, request, jsonify
from flask_cors import CORS
from fuzzy_logic import get_performance_based_on_history, get_student_history
from database.models import insert_user, get_user_by_email

app = Flask(__name__)
CORS(app)

def create_connection():
    return sqlite3.connect('tcc_backend.db')

def adjust_difficulty(is_correct, current_difficulty):
    difficulties = ['easy', 'medium', 'hard']
    current_index = difficulties.index(current_difficulty)

    print(f"Current difficulty: {current_difficulty}")
    print(f"Is correct: {is_correct}")

    if is_correct:
        if current_index < len(difficulties) - 1:
            next_difficulty = difficulties[current_index + 1]
        else:
            next_difficulty = 'hard'
    else:
        if current_index > 0:
            next_difficulty = difficulties[current_index - 1]
        else:
            next_difficulty = 'easy'

    print(f"Next difficulty: {next_difficulty}")
    return next_difficulty

def get_next_question_based_on_difficulty(user_id, difficulty, fallback_attempted=False):
    conn = create_connection()
    cursor = conn.cursor()

    print(f"Buscando próxima questão com dificuldade: {difficulty}")

    cursor.execute('''
        SELECT q.id, q.question_text, q.difficulty, c.id as choice_id, c.choice_text, c.is_correct
        FROM questions q
        JOIN choices c ON q.id = c.question_id
        WHERE q.difficulty = ?
        AND q.id NOT IN (
            SELECT question_id FROM student_progress WHERE user_id = ?
        )
    ''', (difficulty, user_id))

    rows = cursor.fetchall()

    if rows:
        questions = {}
        for row in rows:
            question_id = row[0]
            if question_id not in questions:
                questions[question_id] = {
                    "id": question_id,
                    "question_text": row[1],
                    "difficulty": row[2],
                    "choices": []
                }
            questions[question_id]["choices"].append({
                "id": row[3],
                "choice_text": row[4],
                "is_correct": row[5]
            })
        next_question = list(questions.values())[0]
        print(f"Próxima questão selecionada com dificuldade: {next_question['difficulty']}")
        return next_question
    
    if not fallback_attempted:
        print(f"Sem questões disponíveis para a dificuldade: {difficulty}")
        fallback_difficulty = 'easy' if difficulty == 'medium' else 'medium'
        return get_next_question_based_on_difficulty(user_id, fallback_difficulty, fallback_attempted=True)

    conn.close()
    return {"message": f"Não há questões disponíveis com a dificuldade {difficulty}.", "status": "completed"}

@app.route('/save_progress', methods=['POST'])
def save_progress():
    data = request.json
    user_id = data.get("user_id")
    question_id = data.get("question_id")
    choice_id = data.get("choice_id")
    time_taken = data.get("time_taken")

    try:
        conn = create_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT COUNT(*) FROM student_progress
            WHERE user_id = ? AND question_id = ?
        ''', (user_id, question_id))

        already_answered = cursor.fetchone()[0]

        if already_answered > 0:
            conn.close()
            return jsonify({"message": "Questão já respondida!", "status": "already_answered"}), 200

        cursor.execute('''
            SELECT c.is_correct, q.difficulty
            FROM choices c
            JOIN questions q ON q.id = c.question_id
            WHERE c.id = ?
        ''', (choice_id,))
        is_correct, current_difficulty = cursor.fetchone()

        cursor.execute('''
            INSERT INTO student_progress (user_id, question_id, choice_id, time_taken)
            VALUES (?, ?, ?, ?)
        ''', (user_id, question_id, choice_id, time_taken))

        conn.commit()

        performance_data = get_performance_based_on_history(user_id)
        performance_message = f"Desempenho do estudante: {performance_data['performance']} | Acurácia: {performance_data['accuracy']} | Tempo médio: {performance_data['response_time']} segundos."

        next_difficulty = adjust_difficulty(is_correct, current_difficulty)

        print(f"Nível atual da questão: {current_difficulty}")
        print(f"Nível ajustado da próxima questão: {next_difficulty}")

        next_question = get_next_question_based_on_difficulty(user_id, next_difficulty)

        conn.close()

        return jsonify({
            "message": "Progresso salvo com sucesso!",
            "status": "success",
            "hint": performance_data['message'],
            "performance": performance_data,
            "performance_message": performance_message,
            "next_question": next_question
        }), 201

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Erro ao salvar progresso: {e}\nDetalhes do erro:\n{error_details}")
        return jsonify({
            "message": "Erro ao salvar progresso.",
            "status": "error",
            "details": str(e)
        }), 500

@app.route('/get_next_question', methods=['POST'])
def get_next_question():
    data = request.json
    user_id = data.get("user_id")
    difficulty = data.get("difficulty")

    if not difficulty:
        conn = create_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT q.difficulty
            FROM student_progress sp
            JOIN questions q ON sp.question_id = q.id
            WHERE sp.user_id = ?
            ORDER BY sp.id DESC LIMIT 1
        ''', (user_id,))
        
        last_difficulty = cursor.fetchone()
        difficulty = last_difficulty[0] if last_difficulty else 'easy'
        conn.close()

    next_question = get_next_question_based_on_difficulty(user_id, difficulty)
    
    return jsonify({"question": next_question, "status": "success"}), 200

@app.route('/check_question', methods=['POST'])
def check_question():
    data = request.json
    user_id = data.get("user_id")
    question_id = data.get("question_id")

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT COUNT(*) FROM student_progress
        WHERE user_id = ? AND question_id = ?
    ''', (user_id, question_id))

    count = cursor.fetchone()[0]
    conn.close()

    if count > 0:
        return jsonify({"answered": True})
    else:
        return jsonify({"answered": False})

@app.route('/register', methods=['POST'])
def register_user():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not all([username, email, password]):
        return jsonify({"error": "Todos os campos são obrigatórios"}), 400

    if get_user_by_email(email):
        return jsonify({"error": "E-mail já registrado"}), 400

    insert_user(username, email, password, "student")
    return jsonify({"message": "Usuário registrado com sucesso"}), 201

@app.route('/login', methods=['POST'])
def login_user():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "E-mail e senha são obrigatórios"}), 400

    user = get_user_by_email(email)
    if not user:
        return jsonify({"error": "Usuário não encontrado"}), 404

    if user['password'] != password:
        return jsonify({"error": "Senha incorreta"}), 401

    return jsonify({"message": "Login bem-sucedido"}), 200

@app.route('/questions', methods=['GET'])
def get_questions():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT q.id, q.question_text, c.id, c.choice_text, c.is_correct
        FROM questions q
        JOIN choices c ON q.id = c.question_id
    ''')

    rows = cursor.fetchall()

    questions = {}
    for row in rows:
        question_id = row[0]
        if question_id not in questions:
            questions[question_id] = {
                "id": question_id,
                "question_text": row[1],
                "choices": [],
                "correct_choice": None
            }
        questions[question_id]["choices"].append({
            "id": row[2],
            "choice_text": row[3]
        })
        if row[4]:
            questions[question_id]["correct_choice"] = row[2]

    conn.close()

    return jsonify(list(questions.values()))

if __name__ == "__main__":
    app.run(debug=True)