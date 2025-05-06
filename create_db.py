from project import db, create_app

# Crie a aplicação Flask
app = create_app()

# Crie um contexto de aplicação e chame create_all()
with app.app_context():
    db.create_all()
    print("Tabelas criadas com sucesso!")
