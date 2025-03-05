from gestao_pedidos import app
from gestao_pedidos.database.config import mysql
from gestao_pedidos.models.Admin import Admin
from gestao_pedidos.models.Client import Client
from gestao_pedidos.models.Orders import Orders
import os
from flask import render_template, redirect, url_for, request, flash
from flask_login import login_user, login_required, logout_user, current_user
from flask_login import LoginManager

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM tb_admin WHERE admin_id = %s", (user_id,))
    admin = cursor.fetchone()
    cursor.close()
    if admin:
        return Admin(admin['admin_id'], admin['admin_nome'], admin['admin_email'], admin['admin_senha'])
    return None


@app.route('/')
def index():
    cursor = mysql.connection.cursor()

    cursor.execute("SELECT * FROM tb_admin WHERE admin_email = %s", (os.getenv('EMAIL_ADMIN'),))
    admin = cursor.fetchone()

    if not admin:
        Admin.create_admin(os.getenv('NOME_ADMIN'), os.getenv('EMAIL_ADMIN'), os.getenv('SENHA_ADMIN'))
        print("Administrador padrão criado com sucesso!")

    cursor.close()
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['password']
        admin = Admin.get_by_email(email)
        if admin and admin.verify_password(senha):
            login_user(admin)  
            return redirect(url_for('home'))  
        else:
            flash("Email ou senha incorretos.", "danger")
    return render_template('login.html')

@app.route('/home')
@login_required
def home():
    ordem = request.args.get('ordem', 'asc')
    
    dados = Orders.get_all(ordem)

    return render_template("home.html", dados=dados, ordem=ordem)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))