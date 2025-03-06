from gestao_pedidos import app
from gestao_pedidos.models.Orders import Orders
from gestao_pedidos.database.config import mysql
import MySQLdb
from gestao_pedidos.models.Client import Client
from flask import request, render_template, redirect, url_for, session, flash
from flask_login import login_required

@app.route('/cadastrar_pedido', methods=['GET', 'POST'])
@login_required
def cadastrar_pedido():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM tb_clientes")
        clientes = cursor.fetchall()

        cursor.execute("SELECT * FROM tb_produtos")
        produtos = cursor.fetchall()
        cursor.close()

        if request.method == 'POST':
            data = request.form.get('data')
            cli_id = int(request.form.get('cli_id'))
            produtos_selecionados = []
            total_pedido = 0

            for produto in produtos:
                produto_id = str(produto['pro_id'])
                if produto_id in request.form.getlist('produtos'):
                    quantidade = int(request.form.get(f'quantidade_{produto_id}', 1))


                    estoque_disponivel = produto['pro_quantidade']
                    if quantidade > estoque_disponivel:
                        flash(f"Quantidade de estoque insuficiente para o produto {produto['pro_nome']}! Disponível: {estoque_disponivel}", "danger")
                        return redirect(url_for('cadastrar_pedido'))
                    
                    subtotal = produto['pro_preco'] * quantidade
                    total_pedido += subtotal
                    produtos_selecionados.append({
                        'pro_id': produto['pro_id'],
                        'pro_nome': produto['pro_nome'],
                        'quantidade': quantidade,
                        'subtotal': subtotal
                    })

            novo_pedido = Orders(cli_id=cli_id, data=data, total=total_pedido, produtos=produtos_selecionados)
            resultado = novo_pedido.save()

            flash(resultado['message'], 'success' if resultado['success'] else 'danger')
            return redirect(url_for('listar_pedidos'))

        return render_template('cadastrar_pedido.html', clientes=clientes, produtos=produtos, produtos_selecionados=[], total_pedido=0)

    except Exception as e:
        if "'pro_estoque'" in str(e): 
            flash("Quantidade de estoque invalida!", "danger")

    return redirect(url_for('listar_pedidos'))


@app.route('/listar_pedidos', methods=['GET'])
@login_required
def listar_pedidos():
    ordem = request.args.get('ordem', 'asc')
    nome_cliente = request.args.get('nome', '')

    if ordem not in ['asc', 'desc']:
        ordem = 'asc'

    query = """SELECT ped_id, ped_data, cli_nome, GROUP_CONCAT(pro_nome SEPARATOR ', ') AS produtos, ped_total
               FROM tb_pedidos JOIN tb_clientes ON ped_cli_id = cli_id JOIN tb_proPed ON ped_id = proPed_ped_id
               JOIN tb_produtos ON proPed_pro_id = pro_id WHERE cli_nome LIKE %s GROUP BY ped_id
               ORDER BY ped_id """ + ordem

    cursor = mysql.connection.cursor()
    cursor.execute(query, (f"%{nome_cliente}%",))
    dados = cursor.fetchall()
    cursor.close()

    return render_template('listar_pedidos.html', dados=dados, ordem=ordem, nome_cliente=nome_cliente)

@app.route('/editar_pedido/<int:ped_id>', methods=['GET', 'POST'])
@login_required
def editar_pedido(ped_id):
    cursor = mysql.connection.cursor()
    if request.method == 'POST':
        cli_id = request.form.get('cli_id')
        data = request.form.get('data')


        if not cli_id or not data:
            flash("Por favor, preencha todos os campos.", "danger")
            return redirect(url_for('editar_pedido', ped_id=ped_id))

        cursor.execute("UPDATE tb_pedidos SET ped_cli_id = %s, ped_data = %s WHERE ped_id = %s", (cli_id, data, ped_id))
        mysql.connection.commit()

        flash("Pedido atualizado com sucesso!", "success")
        return redirect(url_for('listar_pedidos'))
    else:
        cursor.execute("SELECT * FROM tb_pedidos WHERE ped_id = %s", (ped_id,))
        pedido = cursor.fetchone()


        cursor.execute("SELECT * FROM tb_clientes")
        clientes = cursor.fetchall()
        cursor.close()


        return render_template('editar_pedido.html', pedido=pedido, clientes=clientes)

@app.route('/excluir_pedido/<int:ped_id>', methods=['GET', 'POST'])
@login_required
def excluir_pedido(ped_id):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM tb_proPed WHERE proPed_ped_id = %s", (ped_id,))
        mysql.connection.commit()
        cursor.execute("DELETE FROM tb_pedidos WHERE ped_id = %s", (ped_id,))
        mysql.connection.commit()
        cursor.close()
        flash("Pedido excluído com sucesso!", "success")
    
    except MySQLdb.Error as e:
        mysql.connection.rollback()
        flash(f"Erro ao excluir pedido: {str(e)}", "danger")
    
    return redirect(url_for('listar_pedidos'))