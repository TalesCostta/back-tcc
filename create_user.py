from database.models import insert_user

def create_new_user():
    username = input("Digite o nome de usuário: ")
    email = input("Digite o e-mail: ")
    password = input("Digite a senha: ")
    role = input("Digite o papel (student, tutor, admin): ")

    insert_user(username, email, password, role)
    print(f"Usuário {username} criado com sucesso!")

if __name__ == "__main__":
    create_new_user()