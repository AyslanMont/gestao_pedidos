from gestao_pedidos import app
from gestao_pedidos.database.config import mysql
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash

class User:
    def __init__(self, id, nome, email):
        self.id = id
        self.nome = nome
        self.email = email

    @classmethod
    def save(cls, nome, email):
        cursor = mysql.connection.cursor()
        INSERT = "INSERT INTO tb_usuarios (usu_nome, usu_email) VALUES (%s, %s)"
        cursor.execute(INSERT, (nome, email))
        mysql.connection.commit()
        cursor.close()
        return True

    @classmethod
    def get(cls, id):
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM tb_usuarios WHERE usu_id = %s", (id,))
        usuario = cursor.fetchone()
        cursor.close()
        if usuario:
            return User(usuario['usu_id'], usuario['usu_nome'], usuario['usu_email'], usuario['usu_senha'], usuario['usu_tipo'])
        return None
    
    @classmethod
    def get_by_email(cls, email):
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM tb_usuarios WHERE usu_email = %s", (email,))
        usuario = cursor.fetchone()
        cursor.close()
        if usuario:
            return User(usuario['usu_id'], usuario['usu_nome'], usuario['usu_email'], usuario['usu_senha'], usuario['usu_tipo'])
        return None

    def verify_password(self, senha):
        return check_password_hash(self.senha, senha)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)
