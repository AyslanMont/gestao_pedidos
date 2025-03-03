from gestao_pedidos import app
from gestao_pedidos.models.Log import Log
from flask import render_template
from flask_login import login_required, current_user

@app.route('/logs')
@login_required
def logs():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    
    logs = Log.get_all_logs()
    return render_template("logs.html", logs=logs)
