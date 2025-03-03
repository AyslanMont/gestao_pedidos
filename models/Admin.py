from werkzeug.security import generate_password_hash, check_password_hash
from gestao_pedidos.database.config import mysql
from flask_login import UserMixin

class Admin(UserMixin):
    def __init__(self, id, nome, email, senha):
        self.id = id
        self.nome = nome
        self.email = email
        self.senha = senha

    @classmethod
    def get_by_email(cls, email):
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM tb_admin WHERE admin_email = %s", (email,))
        admin = cursor.fetchone()
        cursor.close()
        if admin:
            return cls(admin['admin_id'], admin['admin_nome'], admin['admin_email'], admin['admin_senha'])
        return None

    def verify_password(self, senha):
        return check_password_hash(self.senha, senha)

    @staticmethod
    def create_admin(nome, email, senha):
        senha_hash = generate_password_hash(senha)
        cursor = mysql.connection.cursor()
        cursor.execute(
            "INSERT INTO tb_admin (admin_nome, admin_email, admin_senha) VALUES (%s, %s, %s)",
            (nome, email, senha_hash)
        )
        mysql.connection.commit()
        cursor.close()

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)
