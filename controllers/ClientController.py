from gestao_pedidos import app
from gestao_pedidos.database.config import mysql
from gestao_pedidos.models.Client import Client
from flask import request, render_template, redirect, url_for, flash
from flask_login import login_required
from gestao_pedidos.models.Admin import Admin


@app.route('/cadastrar_cliente', methods=['GET', 'POST'])
@login_required
def cadastrar_cliente():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        endereco = request.form['endereco']
        telefone = request.form['telefone']
        client = Client(nome, email, telefone, endereco)
        client.save()

        return redirect(url_for('home'))
    return render_template('cadastrar_cliente.html')





@app.route('/listar_clientes', methods=['GET'])
@login_required
def listar_clientes():
    ordem = request.args.get('ordem', 'asc')
    query = f'SELECT * FROM tb_clientes ORDER BY cli_nome {"ASC" if ordem == "asc" else "DESC"}'
    cursor = mysql.connection.cursor()
    cursor.execute(query)
    dados = cursor.fetchall()
    cursor.close()
    return render_template('listar_clientes.html', dados=dados, ordem=ordem)


@app.route('/editar_cliente/<int:cli_id>', methods=['GET', 'POST'])
@login_required
def editar_cliente(cli_id):
    cursor = mysql.connection.cursor()
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        endereco = request.form['endereco']
        telefone = request.form['telefone']
        cursor.execute("""
            UPDATE tb_clientes 
            SET cli_nome = %s, cli_email = %s, cli_endereco = %s, cli_telefone = %s 
            WHERE cli_id = %s
        """, (nome, email, endereco, telefone, cli_id))
        mysql.connection.commit()
        cursor.close()
        flash("Cliente atualizado com sucesso!", "success")
        return redirect(url_for('listar_clientes'))
    else:
        cursor.execute("SELECT * FROM tb_clientes WHERE cli_id = %s", (cli_id,))
        cliente = cursor.fetchone()
        cursor.close()
        return render_template('editar_cliente.html', cliente=cliente)


@app.route('/excluir_cliente/<int:cli_id>', methods=['GET', 'POST'])
@login_required
def excluir_cliente(cli_id):
    cursor = mysql.connection.cursor()
    
    # Excluir produtos associados aos pedidos do cliente
    cursor.execute("""
        DELETE tb_proPed 
        FROM tb_proPed 
        JOIN tb_pedidos ON tb_proPed.proPed_ped_id = tb_pedidos.ped_id 
        WHERE tb_pedidos.ped_cli_id = %s
    """, (cli_id,))
    mysql.connection.commit()
    
    # Excluir pedidos associados ao cliente
    cursor.execute("DELETE FROM tb_pedidos WHERE ped_cli_id = %s", (cli_id,))
    mysql.connection.commit()
    
    # Excluir o cliente
    cursor.execute("DELETE FROM tb_clientes WHERE cli_id = %s", (cli_id,))
    mysql.connection.commit()
    
    cursor.close()
    flash("Cliente excluído com sucesso!", "success")
    return redirect(url_for('listar_clientes'))
