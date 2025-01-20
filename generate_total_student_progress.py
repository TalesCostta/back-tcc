import sqlite3
import numpy as np
import matplotlib.pyplot as plt

def get_question_statistics_from_db(question_id):
    conn = sqlite3.connect("tcc_backend.db")
    cursor = conn.cursor()
    cursor.execute('''
        SELECT average_time, accuracy_rate
        FROM question_statistics
        WHERE id = ?
    ''', (question_id,))
    stats = cursor.fetchone()
    conn.close()
    return stats if stats else (0, 0)

def get_student_history_from_db(user_id):
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

def calculate_student_performance_from_db(history):
    total_correct = 0
    total_questions = len(history)
    total_time_taken = 0
    total_avg_time = 0
    total_avg_accuracy = 0
    
    for question_id, is_correct, time_taken in history:
        avg_time_taken, avg_accuracy = get_question_statistics_from_db(question_id)
        
        total_correct += is_correct  
        total_time_taken += time_taken  
        total_avg_time += avg_time_taken  
        total_avg_accuracy += avg_accuracy 
    
    average_student_accuracy = (total_correct / total_questions) * 100
    average_student_time = total_time_taken / total_questions
    average_question_time = total_avg_time / total_questions
    average_question_accuracy = total_avg_accuracy / total_questions * 100
    
    performance = {
        'student_accuracy': average_student_accuracy,
        'student_time': average_student_time,
        'average_question_time': average_question_time,
        'average_question_accuracy': average_question_accuracy
    }
    
    return performance

def plot_student_performance(performance):
    labels = ['Acurácia do Estudante', 'Tempo de Resposta do Estudante', 'Acurácia Média das Questões', 'Tempo Médio das Questões']
    student_values = [performance['student_accuracy'], performance['student_time']]
    question_values = [performance['average_question_accuracy'], performance['average_question_time']]
    
    x = np.arange(len(labels) // 2)  
    width = 0.35  
    
    fig, ax = plt.subplots()
    bars1 = ax.bar(x - width/2, student_values, width, label='Estudante')
    bars2 = ax.bar(x + width/2, question_values, width, label='Questões (Média)')
    
    ax.set_xlabel('Métricas de Desempenho')
    ax.set_ylabel('Valores')
    ax.set_title('Comparação do Desempenho do Estudante com as Questões (Média)')
    ax.set_xticks(x)
    ax.set_xticklabels(['Acurácia (%)', 'Tempo de Resposta (s)'])
    ax.legend()
    
    plt.show()

def get_hint_based_on_performance(user_id):
    
    student_history = get_student_history_from_db(user_id)
    
    performance = calculate_student_performance_from_db(student_history)
    
    plot_student_performance(performance)

if __name__ == "__main__":
    get_hint_based_on_performance(1)