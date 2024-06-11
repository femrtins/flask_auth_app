# Recomendação de Livros

## Páginas
página principal
- [ ] deve ter alguma refêrencia para a página de busca, pra poder acessar ela 

página cadastro
- [ ] deve redirecionar para uma pagina dizendo que o usuário está cadastrado
- [ ] poder entrar usando o username 

página do perfil
- [ ] ter as avaliações do livros
- [ ] aparecer uma pagina dos seguidores
  
página de busca
- [ ] a busca deve retornar todoas as recomendaações que tiverem as palavras escritas na busca, busca pela pessoa cadastrada e recomendações dos livros ( página estilo twitter)
- [ ] exibir todas os pedidos de recomendação mais recentes


## Fazer funcionar no linux:

- ```pip3 install virtualenv```

- criar a pasta do venv ```python3 -m venv auth```
- para ativar: ```source auth/bin/activate```
- para desativar: ```deactivate```

- instalar pacotes ```pip install flask flask-sqlalchemy flask-login```
- caso erro: 
```Usage: flask run [OPTIONS] Try 'flask run --help' for help. Error: Could not locate a Flask application. Use the 'flask --app' option, 'FLASK_APP' environment variable, or a 'wsgi.py' or 'app.py' file in the current directory.```

- definir valores:
- ```export FLASK_APP=project```
- ```export FLASK_DEBUG=1```

- Run app live ```flask run```

- Rodar o create_db.py se não existir o db.sqlite ```python3 create_db.py```
