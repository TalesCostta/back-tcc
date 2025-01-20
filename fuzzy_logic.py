import sqlite3
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

def create_performance_fuzzy_system():

    accuracy = ctrl.Antecedent(np.arange(0, 11, 1), 'accuracy')
    response_time = ctrl.Antecedent(np.arange(0, 101, 1), 'response_time')
    performance = ctrl.Consequent(np.arange(0, 11, 1), 'performance')

    accuracy['low'] = fuzz.trimf(accuracy.universe, [0, 0, 4])
    accuracy['medium'] = fuzz.trimf(accuracy.universe, [3, 5, 7])
    accuracy['high'] = fuzz.trimf(accuracy.universe, [6, 10, 10])

    response_time['fast'] = fuzz.trimf(response_time.universe, [0, 0, 20])
    response_time['moderate'] = fuzz.trimf(response_time.universe, [15, 40, 60])
    response_time['slow'] = fuzz.trimf(response_time.universe, [50, 100, 100])

    performance['poor'] = fuzz.trimf(performance.universe, [0, 0, 4])
    performance['average'] = fuzz.trimf(performance.universe, [3, 5, 7])
    performance['good'] = fuzz.trimf(performance.universe, [6, 8, 10])

    rules = [
        ctrl.Rule(accuracy['low'] & response_time['fast'], performance['average']),
        ctrl.Rule(accuracy['low'] & response_time['moderate'], performance['poor']),
        ctrl.Rule(accuracy['low'] & response_time['slow'], performance['poor']),

        ctrl.Rule(accuracy['medium'] & response_time['fast'], performance['good']),
        ctrl.Rule(accuracy['medium'] & response_time['moderate'], performance['average']),
        ctrl.Rule(accuracy['medium'] & response_time['slow'], performance['average']),

        ctrl.Rule(accuracy['high'] & response_time['fast'], performance['good']),
        ctrl.Rule(accuracy['high'] & response_time['moderate'], performance['good']),
        ctrl.Rule(accuracy['high'] & response_time['slow'], performance['good'])
    ]

    control_system = ctrl.ControlSystem(rules)
    return ctrl.ControlSystemSimulation(control_system)


def create_difficulty_fuzzy_system():
    """
    Sistema fuzzy para decidir PRÓXIMA dificuldade (1=easy,2=medium,3=hard)
    com base em 'performance' (0..10).
    """
    performance = ctrl.Antecedent(np.arange(0, 11, 1), 'performance')
    next_diff = ctrl.Consequent(np.arange(1, 4, 0.1), 'next_diff')

    performance['poor'] = fuzz.trimf(performance.universe, [0, 0, 4])
    performance['average'] = fuzz.trimf(performance.universe, [3, 5, 7])
    performance['good'] = fuzz.trimf(performance.universe, [6, 10, 10])

    next_diff['easy'] = fuzz.trimf(next_diff.universe, [1, 1, 2])
    next_diff['medium'] = fuzz.trimf(next_diff.universe, [1, 2, 3])
    next_diff['hard'] = fuzz.trimf(next_diff.universe, [2, 3, 3])

    rules = [
        ctrl.Rule(performance['poor'], next_diff['easy']),
        ctrl.Rule(performance['average'], next_diff['medium']),
        ctrl.Rule(performance['good'], next_diff['hard']),
    ]

    system = ctrl.ControlSystem(rules)
    return ctrl.ControlSystemSimulation(system)


def compute_performance(accuracy_val, response_time_val):

    sys_perf = create_performance_fuzzy_system()
    sys_perf.input['accuracy'] = accuracy_val
    sys_perf.input['response_time'] = response_time_val
    sys_perf.compute()

    perf = round(sys_perf.output['performance'], 2)

    if perf >= 8:
        msg = "Excelente! Continue assim!"
    elif perf >= 7:
        msg = "Bom desempenho! Tente melhorar ainda mais."
    elif perf >= 6:
        msg = "Desempenho médio. Reforce alguns pontos."
    else:
        msg = "Desempenho abaixo do esperado. Estude mais."

    return perf, msg

def get_performance_based_on_history(user_id):
    history = get_student_history(user_id)
    accuracy, avg_response_time = calculate_student_metrics(history)

    performance, message = compute_performance(accuracy, avg_response_time)

    return {
        "performance": round(performance, 2),
        "message": message,
        "accuracy": round(accuracy, 2),
        "response_time": round(avg_response_time, 2)
    }


def get_student_history(user_id):
    conn = sqlite3.connect("tcc_backend.db")
    cursor = conn.cursor()
    cursor.execute('''
        SELECT sp.question_id, c.is_correct, sp.time_taken
        FROM student_progress sp
        JOIN choices c ON sp.choice_id = c.id
        WHERE sp.user_id = ?
    ''', (user_id,))
    history = cursor.fetchall()
    conn.close()
    return history

def calculate_student_metrics(history):
    total_questions = len(history)
    if total_questions == 0:
        return 0, 0, 'ÓTIMO'

    correct_answers = sum(1 for _, is_correct, _ in history if is_correct)
    accuracy = correct_answers / total_questions * 10
    total_time = sum(time_taken for _, _, time_taken in history)
    avg_response_time = total_time / total_questions 
    
    return accuracy, avg_response_time

def compute_next_difficulty(performance_val):
    
    sys_diff = create_difficulty_fuzzy_system()
    sys_diff.input['performance'] = performance_val
    sys_diff.compute()

    nd_float = sys_diff.output['next_diff']
    nd_rounded = round(nd_float)
    if nd_rounded < 1:
        nd_rounded = 1
    elif nd_rounded > 3:
        nd_rounded = 3
    return nd_rounded