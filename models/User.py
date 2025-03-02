from gestao_pedidos import app
from gestao_pedidos.database.config import mysql
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin):
    def __init__(self, id, nome, email, senha, tipo):
        self.id = id
        self.nome = nome
        self.email = email
        self.senha = senha
        self.tipo = tipo  # 'admin' ou 'user'

    @classmethod
    def save(self, nome, email, senha_hash, tipo='user'):
        cursor = mysql.connection.cursor()
        if tipo == 'admin':
            INSERT = "INSERT INTO tb_admin (admin_nome, admin_email, admin_senha) VALUES (%s, %s, %s)"
            cursor.execute(INSERT, (nome, email, senha_hash))
        else:
            INSERT = "INSERT INTO tb_usuarios (usu_nome, usu_email, usu_senha) VALUES (%s, %s, %s)"
            cursor.execute(INSERT, (nome, email, senha_hash))
        mysql.connection.commit()
        cursor.close()
        return True

    @classmethod
    def get(cls, id):
        cursor = mysql.connection.cursor()

        cursor.execute("SELECT * FROM tb_admin WHERE admin_id = %s", (id,))
        admin = cursor.fetchone()
        if admin:
            cursor.close()
            return User(admin['admin_id'], admin['admin_nome'], admin['admin_email'], admin['admin_senha'], 'admin')

        
        cursor.execute("SELECT * FROM tb_usuarios WHERE usu_id = %s", (id,))
        usuario = cursor.fetchone()
        if usuario:
            cursor.close()
            return User(usuario['usu_id'], usuario['usu_nome'], usuario['usu_email'], usuario['usu_senha'], 'user')

        cursor.close()
        return None
    
    @classmethod
    def get_by_email(cls, email):
        cursor = mysql.connection.cursor()

        cursor.execute("SELECT * FROM tb_usuarios WHERE usu_email = %s", (email,))
        usuario = cursor.fetchone()
        if usuario:
            cursor.close()
            return User(usuario['usu_id'], usuario['usu_nome'], usuario['usu_email'], usuario['usu_senha'], usuario['usu_tipo'])

        cursor.close()
        return None

    def verify_password(self, senha):
        return check_password_hash(self.senha, senha)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)