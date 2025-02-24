from gestao_pedidos import app
from gestao_pedidos.database.config import mysql
from gestao_pedidos.models.User import User
from gestao_pedidos.models.Orders import Orders
from flask import render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/home')
@login_required
def home():
    ordem = request.args.get('ordem', 'asc')
    
    dados = Orders.get_all(ordem)

    return render_template("home.html", dados=dados, ordem=ordem)



@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['password']
        user = User.get_by_email(email)
        senha_hash = generate_password_hash(senha)

        if user:
            flash("O usuário já está cadastrado!", "danger")
        else:
            user = User.save(nome, email, senha_hash)
            flash("Registro efetuado com sucesso! Use suas credenciais para fazer login.", "success")
            return redirect(url_for("login"))
    
    return render_template("register.html")

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form['email']
        senha = request.form['password']
        user = User.get_by_email(email)
        if user and check_password_hash(user.senha, senha):
            login_user(user)
            return redirect(url_for("home"))
        else:
            flash("Email ou senha incorretos. Verifique suas credenciais e tente novamente.", "danger")
    
    return render_template("login.html")

@app.route("/logout")
def logout():
    if current_user.is_authenticated:
        logout_user()
    return redirect(url_for("login"))