from gestao_pedidos import app
from gestao_pedidos.models.Orders import Orders
from gestao_pedidos.database.config import mysql
from gestao_pedidos.models.Client import Client
from flask import request, render_template, redirect, url_for, session, flash
from flask_login import login_required, current_user

@app.route('/cadastrar_pedido', methods=['GET', 'POST'])
def cadastrar_pedido():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    # Obter clientes e produtos cadastrados
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM tb_clientes")
    clientes = cursor.fetchall()

    cursor.execute("SELECT * FROM tb_produtos")
    produtos = cursor.fetchall()
    cursor.close()

    if request.method == 'POST':
        data = request.form.get('data')
        cli_id = int(request.form.get('cli_id'))  # Aqui estamos assumindo que cli_id será passado como um número inteiro
        produtos_selecionados = []
        total_pedido = 0

        # Processar produtos selecionados
        for produto in produtos:
            produto_id = str(produto['pro_id'])
            if produto_id in request.form.getlist('produtos'):
                quantidade = int(request.form.get(f'quantidade_{produto_id}', 1))
                subtotal = produto['pro_preco'] * quantidade
                total_pedido += subtotal
                produtos_selecionados.append({
                    'pro_id': produto['pro_id'],
                    'pro_nome': produto['pro_nome'],
                    'quantidade': quantidade,
                    'subtotal': subtotal
                })

        # Salvar o pedido no banco
        novo_pedido = Orders(cli_id=cli_id, data=data, total=total_pedido, produtos=produtos_selecionados)
        resultado = novo_pedido.save()

        flash(resultado['message'], 'success' if resultado['success'] else 'danger')
        return redirect(url_for('listar_pedidos'))

    return render_template('cadastrar_pedido.html', clientes=clientes, produtos=produtos, produtos_selecionados=[], total_pedido=0)

@app.route('/listar_pedidos', methods=['GET'])
def listar_pedidos():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    ordem = request.args.get('ordem', 'asc')
    dados = Orders.get_all(ordem)
    if dados is None:
        dados = []
    return render_template('listar_pedidos.html', dados=dados, ordem=ordem)

@app.route('/editar_pedido/<int:ped_id>', methods=['GET', 'POST'])
def editar_pedido(ped_id):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    cursor = mysql.connection.cursor()
    if request.method == 'POST':
        # Recuperar os dados do formulário
        cli_id = request.form.get('cli_id')
        data = request.form.get('data')

        # Verificar se cli_id e data foram enviados corretamente
        if not cli_id or not data:
            flash("Por favor, preencha todos os campos.", "danger")
            return redirect(url_for('editar_pedido', ped_id=ped_id))

        # Atualizar o pedido no banco de dados
        cursor.execute("UPDATE tb_pedidos SET ped_cli_id = %s, ped_data = %s WHERE ped_id = %s", (cli_id, data, ped_id))
        mysql.connection.commit()

        flash("Pedido atualizado com sucesso!", "success")
        return redirect(url_for('listar_pedidos'))
    else:
        # Obter o pedido atual
        cursor.execute("SELECT * FROM tb_pedidos WHERE ped_id = %s", (ped_id,))
        pedido = cursor.fetchone()

        # Obter a lista de clientes
        cursor.execute("SELECT * FROM tb_clientes")
        clientes = cursor.fetchall()
        cursor.close()

        # Passar o pedido e os clientes para o template
        return render_template('editar_pedido.html', pedido=pedido, clientes=clientes)

@app.route('/excluir_pedido/<int:ped_id>', methods=['GET', 'POST'])
@login_required
def excluir_pedido(ped_id):
    cursor = mysql.connection.cursor()
    
    # Excluir produtos associados ao pedido
    cursor.execute("DELETE FROM tb_proPed WHERE proPed_ped_id = %s", (ped_id,))
    mysql.connection.commit()
    
    # Excluir o pedido
    cursor.execute("DELETE FROM tb_pedidos WHERE ped_id = %s", (ped_id,))
    mysql.connection.commit()
    
    cursor.close()
    flash("Pedido excluído com sucesso!", "success")
    return redirect(url_for('listar_pedidos'))
