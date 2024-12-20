from flask import Blueprint, render_template, request, redirect, url_for, session, make_response, flash
from werkzeug.security import check_password_hash, generate_password_hash
import json
from model import db, Usuario, Disco

questController = Blueprint("questoes", __name__)

# Verificação de tipo de usuário
def verificar_funcionario():
    return session.get("tipo") == "funcionario"

@questController.route("/")
def index():
    return render_template("login.html")

@questController.route("/verifica", methods=["POST"])
def verifica():
    email = request.form.get("email")
    senha = request.form.get("senha")

    usuario = Usuario.query.filter_by(email=email).first()

    if usuario and check_password_hash(usuario.senha, senha):
        session["email"] = usuario.email
        session["tipo"] = usuario.tipo
        return redirect(url_for("questoes.catalogo"))

    return "E-mail ou senha incorretos", 401

@questController.route("/catalogo")
def catalogo():
    shopping_cart = request.cookies.get("shopping_cart")
    cart_ids = json.loads(shopping_cart) if shopping_cart else []

    # Buscar discos do banco que estão no carrinho
    discos_carrinho = Disco.query.filter(Disco.id.in_(cart_ids)).all()
    total = sum(disco.preco for disco in discos_carrinho)

    # Buscar todos os discos disponíveis
    todos_discos = Disco.query.all()

    return render_template("catalogo.html", cart=discos_carrinho, discos=todos_discos, total=total)

@questController.route("/add_to_cart", methods=["POST"])
def add_to_cart():
    disco_id = request.form.get("disco_id")
    cart = json.loads(request.cookies.get("shopping_cart", "[]"))
    cart.append(int(disco_id))  # Adicionar o ID do disco ao carrinho
    resp = make_response(redirect(url_for("questoes.catalogo")))
    resp.set_cookie("shopping_cart", json.dumps(cart))
    return resp

@questController.route("/clear_cart")
def clear_cart():
    resp = make_response(redirect(url_for("questoes.catalogo")))
    resp.set_cookie("shopping_cart", "", expires=0)
    return resp

@questController.route("/pagamento")
def pagamento():
    return render_template("pagamento.html")

@questController.route("/logout")
def logout():
    session.pop("email", None)
    session.pop("tipo", None)
    return redirect(url_for("questoes.index"))

# Gerenciamento de discos para funcionários
@questController.route("/discos", methods=["GET", "POST"])
def gerenciar_discos():
    if not verificar_funcionario():
        return "Acesso negado. Apenas funcionários podem acessar esta página.", 403

    if request.method == "POST":
        artista = request.form.get("artista")
        nome_album = request.form.get("nome_album")
        preco = request.form.get("preco")

        # Adicionar novo disco
        novo_disco = Disco(artista=artista, nome_album=nome_album, preco=float(preco))
        db.session.add(novo_disco)
        db.session.commit()

        flash("Disco adicionado com sucesso!")
        return redirect(url_for("questoes.gerenciar_discos"))

    return render_template("discos.html", discos=Disco.query.all())

@questController.route("/configuracoes", methods=["GET", "POST"])
def configuracoes():
    if not verificar_funcionario():
        return "Acesso negado. Apenas funcionários podem acessar esta página.", 403

    if request.method == "POST":
        if "adicionar_usuario" in request.form:
            nome = request.form.get("nome")
            email = request.form.get("email")
            senha = request.form.get("senha")
            tipo = request.form.get("tipo")

            # Adicionar usuário
            novo_usuario = Usuario(
                nome=nome,
                email=email,
                senha=generate_password_hash(senha),
                tipo=tipo
            )
            db.session.add(novo_usuario)
            db.session.commit()
            flash("Usuário adicionado com sucesso!")

        elif "excluir_disco" in request.form:
            disco_id = request.form.get("disco_id")
            disco = Disco.query.get(disco_id)
            if disco:
                db.session.delete(disco)
                db.session.commit()
                flash("Disco excluído com sucesso!")

        elif "excluir_usuario" in request.form:
            usuario_id = request.form.get("usuario_id")
            usuario = Usuario.query.get(usuario_id)
            if usuario:
                db.session.delete(usuario)
                db.session.commit()
                flash("Usuário excluído com sucesso!")

        return redirect(url_for("questoes.configuracoes"))

    return render_template("funcionario.html", discos=Disco.query.all(), usuarios=Usuario.query.all())
