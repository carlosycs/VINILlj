from flask import Flask, render_template, session, redirect, url_for, request
from controller import questController
from model import db, Usuario, Disco 
import json

app = Flask(__name__)
app.secret_key = "chavesecreta123"

# Configuração do banco de dados
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///banco.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

app.register_blueprint(questController)

@app.route("/")
def hello_world():
    return render_template("login.html")

rotas_publicas = ["questoes.index", "questoes.verifica", "inicializar_db", "inicializar_disco"]

@app.before_request
def verificarIdentifica():
    if request.endpoint in rotas_publicas:
        return

    if "email" in session:
        return

    return redirect(url_for("questoes.index"))

@app.route("/inicializar_db")
def inicializar_db():
    # Verificar se o funcionário já existe
    if Usuario.query.filter_by(email="cadu2007edu@gmail.com").first():
        return "Funcionário já foi adicionado!"

    # Criar um funcionário
    from werkzeug.security import generate_password_hash
    funcionario = Usuario(
        nome="Carlos",
        email="cadu2007edu@gmail.com",
        senha=generate_password_hash("adm123"),
        tipo="funcionario"
    )

    # Adicionar ao banco de dados
    db.session.add(funcionario)
    db.session.commit()

    return "Funcionário inicial adicionado com sucesso!"

# Rota para inicializar discos
@app.route("/inicializar_disco")
def inicializar_disco():
    # Verificar se o disco já foi adicionado
    if Disco.query.filter_by(nome_album="The Dark Side of the Moon").first():
        return "Disco já foi adicionado!"  # Se já existir, não adiciona novamente

    # Adicionar discos (exemplo)
    disco1 = Disco(
        artista="Pink Floyd",
        nome_album="The Dark Side of the Moon",
        preco=99.90
    )

    disco2 = Disco(
        artista="The Beatles",
        nome_album="Abbey Road",
        preco=79.90
    )

    # Adicionar ao banco de dados
    db.session.add(disco1)
    db.session.add(disco2)
    db.session.commit()

    return "Discos adicionados com sucesso!"

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Cria as tabelas no banco de dados
    app.run(debug=True)
