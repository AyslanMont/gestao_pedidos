from gestao_pedidos import app
from gestao_pedidos.database.config import mysql
from gestao_pedidos.models.User import User
from gestao_pedidos.models.Orders import Orders
import os
from flask import render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user

@app.route('/')
def index():
    cursor = mysql.connection.cursor()

    cursor.execute("SELECT * FROM tb_admin WHERE admin_email = %s", (os.getenv('EMAIL_ADMIN'),))
    admin = cursor.fetchone()

    if not admin:
        senha_hash = generate_password_hash(os.getenv('SENHA_ADMIN'))
        cursor.execute(
            "INSERT INTO tb_admin (admin_nome, admin_email, admin_senha) VALUES (%s, %s, %s)",
            (os.getenv('NOME_ADMIN'), os.getenv('EMAIL_ADMIN'), senha_hash)
        )
        mysql.connection.commit()
        print("Administrador padrão criado com sucesso!")

    cursor.close()
    return render_template('index.html')

@app.route('/home')
@login_required
def home():
    ordem = request.args.get('ordem', 'asc')
    
    dados = Orders.get_all(ordem)

    return render_template("home.html", dados=dados, ordem=ordem)



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['password']
        user = User.get_by_email(email)
        if user and user.verify_password(senha):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash("Email ou senha incorretos. Verifique suas credenciais e tente novamente.", "danger")
    return render_template('login.html')

@app.route("/logout")
def logout():
    if current_user.is_authenticated:
        logout_user()
    return redirect(url_for("login"))