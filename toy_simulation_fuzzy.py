import sqlite3
import random
import statistics
from fuzzy_logic import compute_performance, compute_next_difficulty
from generate_graphs import (
    plot_student_performance_bar,
    plot_performance_evolution,
    plot_heatmap,
    plot_radar,
    plot_boxplot,
    plot_correlation_scatter,
    plot_pie
)
import seaborn as sns
import numpy as np

DB_PATH = "tcc_backend.db"

def parse_accuracy_rate(rate_value):

    if isinstance(rate_value, (float, int)):
        return float(rate_value)
    rate_str = rate_value.strip()
    if rate_str.endswith('%'):
        rate_str = rate_str.replace('%','')
        return float(rate_str) / 100.0
    else:
        return float(rate_str)

def get_questions_from_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, question_text, difficulty, average_time, accuracy_rate
        FROM questions
    """)

    all_q = []
    for row in cursor.fetchall():
        q_id, q_text, diff, avg_time, acc_anytype = row
        avg_t = float(avg_time)
        acc_val = parse_accuracy_rate(acc_anytype)

        all_q.append({
            "id": q_id,
            "text": q_text,
            "difficulty": diff,
            "average_time": avg_t,
            "accuracy_rate": acc_val
        })
    conn.close()
    return all_q

def simulate():
    all_questions = get_questions_from_db()

    questions_by_diff = {
        "easy":   [],
        "medium": [],
        "hard":   []
    }
    for q in all_questions:
        if q["difficulty"] in questions_by_diff:
            questions_by_diff[q["difficulty"]].append(q)
        else:
            pass

    students = (
        [{"id": i, "group": "excellent"} for i in range(1, 6)] +
        [{"id": i, "group": "medium"} for i in range(6, 26)] +
        [{"id": i, "group": "low"} for i in range(26, 36)]
    )

    accuracy_ranges = {
        "excellent": (0.95, 1.0),
        "medium":    (0.65, 0.85),
        "low":       (0.10, 0.50)
    }

    diff_map = {1: "easy", 2: "medium", 3: "hard"}

    NUM_QUESTIONS = 110
    results = []

    performance_data = {"x": [], "y": []}
    evolution_data = {}
    heatmap_matrix = []
    radar_data = {"Taxa de Acertos (%)": [], "Tempo Médio (s)": [], "Performance Média": []}
    boxplot_data = {"easy": [], "medium": [], "hard": []}
    scatter_x = []
    scatter_y = []
    pie_data = {"easy": 0, "medium": 0, "hard": 0}

    for student in students:
        sid = student["id"]
        group = student["group"]

        base_acc = random.uniform(*accuracy_ranges[group])

        current_diff_num = 2
        acertos = 0
        tempos = []
        perf_history = []
        msg_history = []
        student_heatmap = [0, 0, 0]

        for _ in range(NUM_QUESTIONS):
            diff_str = diff_map[current_diff_num]
            pool = questions_by_diff[diff_str]
            if pool:
                chosen_q = random.choice(pool)
            else:
                chosen_q = None

            if chosen_q:
                pie_data[diff_str] += 1
                student_heatmap[current_diff_num - 1] += 1

                final_prob = base_acc * chosen_q["accuracy_rate"]
                correct = (random.random() < final_prob)
                if correct:
                    acertos += 1

                question_time = chosen_q["average_time"]
                if group == "excellent":
                    question_time *= 0.8
                elif group == "low":
                    question_time *= 1.3

                time_spent = random.uniform(question_time * 0.9, question_time * 1.1)
                tempos.append(time_spent)
                boxplot_data[diff_str].append(time_spent)
            else:
                correct = (random.random() < base_acc)
                if correct:
                    acertos += 1
                time_spent = random.uniform(5, 15)
                tempos.append(time_spent)

            answered = len(tempos)
            accuracy_10 = (acertos / answered) * 10
            avg_time = statistics.mean(tempos)

            perf, msg = compute_performance(accuracy_10, avg_time)
            perf_history.append(perf)
            msg_history.append(msg)

            next_diff_num = compute_next_difficulty(perf)
            current_diff_num = next_diff_num

        final_acc_percent = round((acertos / NUM_QUESTIONS) * 100, 2)
        final_avg_time = round(statistics.mean(tempos), 2)
        final_perf = perf_history[-1]

        performance_data["x"].append(sid)
        performance_data["y"].append(final_perf)
        evolution_data[f"Estudante {sid}"] = {"x": list(range(1, len(perf_history) + 1)), "y": perf_history}
        scatter_x.extend([current_diff_num] * len(tempos))
        scatter_y.extend([final_acc_percent] * len(tempos))

        results.append({
            "student_id": sid,
            "group": group,
            "acertos": acertos,
            "accuracy_percent": final_acc_percent,
            "avg_time": final_avg_time,
            "final_performance": final_perf,
            "perf_history": perf_history
        })

        heatmap_matrix.append(student_heatmap)
        radar_data["Taxa de Acertos (%)"].append(final_acc_percent)
        radar_data["Tempo Médio (s)"].append(final_avg_time)
        radar_data["Performance Média"].append(final_perf)

    if not heatmap_matrix:
        print("Matriz do heatmap vazia! Verifique os dados dos estudantes.")
        return

    grouped_results = {"excellent": [], "medium": [], "low": []}
    for r in results:
        grouped_results[r["group"]].append(r)


    plot_student_performance_bar(
        data=performance_data,
        title="Desempenho do Estudante por Questão",
        xlabel="Estudantes",
        ylabel="Performance",
        filename="desempenho_estudante.png"
    )

    plot_performance_evolution(
        data=evolution_data,
        title="Evolução do Desempenho por Grupo",
        xlabel="Tentativas",
        ylabel="Performance",
        filename="evolucao_desempenho.png"
    )

    plot_heatmap(
        data=np.array(heatmap_matrix),
        title="Ajuste de Dificuldade por Estudante",
        xlabel="Níveis de Dificuldade (1=Fácil, 3=Difícil)",
        ylabel="Estudantes",
        filename="ajuste_dificuldade_heatmap.png"
    )

    radar_labels = ["Taxa de Acertos (%)", "Tempo Médio (s)", "Performance Média"]
    radar_values = []

    for group in ["excellent", "medium", "low"]:
        group_results = grouped_results[group]
        radar_values.append([
            statistics.mean([r["accuracy_percent"] for r in group_results]),
            statistics.mean([r["avg_time"] for r in group_results]),
            statistics.mean([r["final_performance"] for r in group_results])
        ])

    plot_radar(
        data=radar_values,
        labels=radar_labels,
        title="Comparativo de Indicadores por Grupo",
        filename="comparativo_indicadores_radar.png"
    )

    plot_boxplot(
        data=boxplot_data,
        title="Distribuição do Tempo de Resposta por Dificuldade",
        xlabel="Níveis de Dificuldade",
        ylabel="Tempo de Resposta (s)",
        filename="distribuicao_boxplot.png"
    )

    plot_correlation_scatter(
        x=scatter_x,
        y=scatter_y,
        xlabel="Níveis de Dificuldade",
        ylabel="Taxa de Acertos (%)",
        title="Correlação entre Dificuldade e Taxa de Acertos",
        filename="correlacao_dificuldade_desempenho.png"
    )

    plot_pie(
        data=[pie_data["easy"], pie_data["medium"], pie_data["hard"]],
        labels=["Fácil", "Médio", "Difícil"],
        title="Distribuição de Dificuldades",
        filename="distribuicao_dificuldades_pizza.png"
    )

if __name__ == "__main__":
    simulate()