from gestao_pedidos import app
from flask_mysqldb import MySQL
import os


app.secret_key = str(os.get("SECRET_KEY"))
app.config['MYSQL_HOST'] = os.getenv("MYSQL_HOST")
app.config['MYSQL_PORT'] = int(os.getenv("MYSQL_PORT"))
app.config['MYSQL_USER'] = os.getenv("MYSQL_USER")
app.config['MYSQL_PASSWORD'] = os.getenv("MYSQL_PASSWORD")
app.config['MYSQL_DB'] = os.getenv("MYSQL_DB")
app.config['MYSQL_CURSORCLASS'] = os.getenv("MYSQL_CURSORCLASS")

mysql = MySQL(app)