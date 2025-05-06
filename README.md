# Rede Social de Livros (com Flask)

Este é um projeto de desenvolvimento web utilizando o framework Flask, que simula uma rede social voltada para leitores. Usuários podem avaliar livros, escrever resenhas e interagir com outros leitores.

## Funcionalidades

- Cadastro e login de usuários
- Perfil de usuário com suas avaliações
- Busca de livros
- Publicação de resenhas e avaliações
- Comentários e interações entre usuários
- Integração com a API do Google Books
- Interface responsiva com HTML/CSS e Bootstrap

## Tecnologias usadas

- Python 3.x
- Flask
- SQLite (ou outro banco relacional)
- SQLAlchemy (ORM)
- Bootstrap (estilização)
- Google Books API

## Requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

## Como rodar o projeto localmente

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/rede-social-livros.git
cd rede-social-livros
```

### 2. Crie um ambiente virtual

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate   # Windows
deactivate # Para desativar
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure o banco de dados

```bash
python3 create_db.py
```

### 5. Inicie o servidor

```bash
flask run
```

Acesse o app em `http://127.0.0.1:5000`.

## Estrutura do Projeto

```
rede_social_livros/
├── app/
│   ├── templates/
│   ├── static/
│   ├── auth.py
|   ├── main.py
│   ├── models.py
│   └── __init__.py
├── create_db.py
└── requirements.txt
```

