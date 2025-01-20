```markdown
# Backend - Projeto TCC

Este repositório contém o código do backend para o projeto de TCC. O backend foi desenvolvido utilizando `Flask` e `SQLite` como banco de dados, além de outras bibliotecas para suporte ao desenvolvimento.

## Requisitos

Antes de iniciar o projeto, certifique-se de ter os seguintes softwares instalados:

- Python 3.9 ou superior
- `pip` (gerenciador de pacotes do Python)

## Instalação e Configuração

1. **Clone o repositório**:

   ```bash
   git clone https://github.com/talescostta/backend-tcc.git
   cd backend-tcc
   ```

2. **Crie um ambiente virtual**:

   É recomendado usar um ambiente virtual para isolar as dependências do projeto:

   ```bash
   python3 -m venv env
   ```

3. **Ative o ambiente virtual**:

   - No **macOS/Linux**:

     ```bash
     source env/bin/activate
     ```

   - No **Windows**:

     ```bash
     .\env\Scripts\activate
     ```

4. **Instale as dependências**:

   No ambiente virtual, execute o comando para instalar as bibliotecas necessárias:

   ```bash
   pip install -r requirements.txt
   ```

5. **Crie o banco de dados**:

   O projeto utiliza um banco de dados SQLite. Para criar as tabelas, execute o seguinte script:

   ```bash
   python3 create_tables.py
   ```

   Isso criará as tabelas necessárias, como `users`, `questions`, `choices`, `student_progress` e `feedback`.

6. **Inserir dados no banco de dados (opcional)**:

   Se você quiser inserir perguntas iniciais no banco, execute o script:

   ```bash
   python3 insert_question_database.py
   ```

## Executando o Backend

1. **Inicie o servidor Flask**:

   Com o ambiente virtual ativo e o banco de dados configurado, inicie o servidor Flask com o comando:

   ```bash
   flask run
   ```

   O servidor estará rodando em [http://127.0.0.1:5000](http://127.0.0.1:5000).

## Endpoints Disponíveis

Aqui estão os principais endpoints disponíveis na API:

- `GET /questions` - Retorna uma lista de questões para o estudante responder.
- `POST /save_progress` - Salva o progresso do estudante.
- `POST /get_hint` - Gera dicas utilizando lógica fuzzy com base no progresso do estudante.

## Testando a API

Você pode testar a API utilizando o `Postman` ou qualquer outra ferramenta para fazer requisições HTTP.

## Contribuindo

Se você deseja contribuir com o projeto, por favor, abra um Pull Request ou crie uma issue com suas sugestões ou problemas encontrados.

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para mais detalhes.
```

### Arquivos adicionais:
- **`requirements.txt`**: Este arquivo deve conter as bibliotecas que o projeto utiliza. Exemplo:

```txt
Flask==2.0.1
Flask-Cors==3.0.10
numpy==1.21.0
scipy==1.7.0
scikit-fuzzy==0.4.2
matplotlib==3.4.2
```