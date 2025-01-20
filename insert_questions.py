import sqlite3
import csv

def create_connection():
    """Cria uma conexão com o banco de dados."""
    return sqlite3.connect('tcc_backend.db')

def insert_data_from_csv(questions_csv, choices_csv):
    """Insere os dados de arquivos CSV no banco de dados."""
    conn = create_connection()
    cursor = conn.cursor()

    with open(questions_csv, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            cursor.execute('''
                INSERT INTO questions (id, question_text, difficulty, average_time, accuracy_rate)
                VALUES (?, ?, ?, ?, ?)
            ''', (row['id'], row['question_text'], row['difficulty'], row['average_time'], row['accuracy_rate']))

    with open(choices_csv, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            cursor.execute('''
                INSERT INTO choices (id, question_id, choice_text, is_correct)
                VALUES (?, ?, ?, ?)
            ''', (row['id'], row['question_id'], row['choice_text'], row['is_correct']))

    conn.commit()
    conn.close()
    print("Dados inseridos com sucesso!")

def main():
    questions_csv = './Questions_Database.csv'
    choices_csv = './Choices_Database.csv'

    insert_data_from_csv(questions_csv, choices_csv)

if __name__ == "__main__":
    main()