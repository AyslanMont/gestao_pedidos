from gestao_pedidos import app
from gestao_pedidos.models.Log import Log
from flask import render_template
from flask_login import login_required

@app.route('/logs')
@login_required
def logs():
    logs = Log.get_all_logs()
    return render_template("logs.html", logs=logs)
