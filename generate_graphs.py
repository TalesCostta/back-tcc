import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import random

def plot_student_performance_bar(data, title, xlabel, ylabel, filename):

    plt.figure(figsize=(10, 6))
    plt.bar(data["x"], data["y"], color='skyblue', edgecolor='black')
    plt.title(title, fontsize=14)
    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    plt.xticks(data["x"])
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

def plot_performance_evolution(data, title, xlabel, ylabel, filename):
    excellent_students = {k: v for k, v in data.items() if "Estudante" in k and int(k.split()[1]) in range(1, 6)}
    medium_students = {k: v for k, v in data.items() if "Estudante" in k and int(k.split()[1]) in range(6, 26)}
    low_students = {k: v for k, v in data.items() if "Estudante" in k and int(k.split()[1]) in range(26, 36)}

    selected_students = {}
    selected_students.update(random.sample(excellent_students.items(), min(3, len(excellent_students))))
    selected_students.update(random.sample(medium_students.items(), min(4, len(medium_students))))
    selected_students.update(random.sample(low_students.items(), min(3, len(low_students))))

    plt.figure(figsize=(10, 6))
    
    for label, values in selected_students.items():
        student_id = label.split()[1]
        
        if int(student_id) in range(1, 6):
            group_name = "Excellent"
        elif int(student_id) in range(6, 26):
            group_name = "Medium"
        else:
            group_name = "Low"

        new_label = f"Estudante {student_id} (Grupo {group_name})"
        
        plt.plot(values["x"], values["y"], marker='o', label=new_label)

    plt.title(title, fontsize=14)
    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

def plot_heatmap(data, title, xlabel, ylabel, filename):

    plt.figure(figsize=(12, 8))
    sns.heatmap(data, annot=True, fmt="d", cmap="coolwarm", cbar=True)
    plt.title(title, fontsize=14)
    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

def plot_radar(data, labels, title, filename):

    num_vars = len(labels)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()

    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))

    for i, group_data in enumerate(data):
        values = group_data + group_data[:1]

        ax.plot(angles, values, linewidth=1, linestyle='solid', label=f"Grupo {i + 1}")
        ax.fill(angles, values, alpha=0.25)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)

    ax.set_yticks([2, 4, 6, 8])
    ax.set_yticklabels(["2", "4", "6", "8"], color="grey", size=10)

    plt.title(title, size=14, color="blue", y=1.1)
    plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
    plt.savefig(filename)
    plt.close()

def plot_boxplot(data, title, xlabel, ylabel, filename):

    plt.figure(figsize=(10, 6))
    sns.boxplot(data=data, palette="Set2")
    plt.title(title, fontsize=14)
    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

def plot_correlation_scatter(x, y, xlabel, ylabel, title, filename):

    plt.figure(figsize=(10, 6))
    sns.scatterplot(x=x, y=y, s=100, alpha=0.7, edgecolor='black')
    sns.regplot(x=x, y=y, scatter=False, color='red')
    plt.title(title, fontsize=14)
    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

def plot_pie(data, labels, title, filename):

    plt.figure(figsize=(8, 8))
    plt.pie(data, labels=labels, autopct='%1.1f%%', startangle=140, colors=sns.color_palette("Set3"))
    plt.title(title, fontsize=14)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()