from gestao_pedidos import app
from gestao_pedidos.models.Products import Products
from flask import request, redirect, url_for, render_template, session, flash
from gestao_pedidos.database.config import mysql
from flask_login import  login_required



@app.route('/cadastrar_produto', methods=['GET', 'POST'])
@login_required
def cadastrar_produto():
    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form['descricao']
        preco = request.form['precouni']
        quantidade = request.form['quantidade']

        product = Products(nome, descricao, preco, quantidade)
        product.save()

        return redirect(url_for('home'))
    return render_template('cadastrar_produto.html')



@app.route('/listar_produtos', methods=['GET', 'POST'])
@login_required
def listar_produtos():
    # Inicializa o carrinho na sessão, se ainda não existir
    if 'produtos_adicionados' not in session:
        session['produtos_adicionados'] = []

    if request.method == 'POST':
        # Obtém os dados do produto enviados pelo formulário
        pro_id = request.form['pro_id']
        pro_nome = request.form['pro_nome']
        pro_preco = float(request.form['pro_preco'])
        quantidade = int(request.form['quantidade'])  # Adicionando a quantidade do produto

        # Verificar se o produto já existe no carrinho
        produto_existente = next((prod for prod in session['produtos_adicionados'] if prod['pro_id'] == pro_id), None)

        if produto_existente:
            # Atualizar a quantidade e o subtotal se o produto já estiver no carrinho
            valor = int(produto_existente['pro_qdproduto'])
            valor2 = valor + quantidade
            produto_existente['pro_qdproduto'] = valor2
            produto_existente['pro_subtotal'] = produto_existente['pro_qdproduto'] * produto_existente['pro_preco']
        else:
            # Caso o produto não exista, adicionar um novo com quantidade e subtotal
            produto = {
                'pro_id': pro_id,
                'pro_nome': pro_nome,
                'pro_preco': pro_preco,
                'pro_qdproduto': quantidade,
                'pro_subtotal': pro_preco * quantidade  # Calculando o subtotal
            }
            session['produtos_adicionados'].append(produto)

        session.modified = True  # Marca a sessão como modificada

        return redirect(url_for('listar_produtos'))  # Evita reenvio do formulário

    # Consulta os produtos no banco
    ordem = request.args.get('ordem', 'asc')
    query = f'SELECT * FROM tb_produtos ORDER BY pro_nome {"ASC" if ordem == "asc" else "DESC"}'
    cursor = mysql.connection.cursor()
    cursor.execute(query)
    dados = cursor.fetchall()
    cursor.close()

    return render_template('listar_produtos.html', dados=dados, ordem=ordem)


@app.route('/editar_produto/<int:pro_id>', methods=['GET', 'POST'])
@login_required
def editar_produto(pro_id):
    cursor = mysql.connection.cursor()

    # Se for uma requisição GET, exibe os dados para edição
    if request.method == 'GET':
        # Buscar o produto
        cursor.execute("SELECT * FROM tb_produtos WHERE pro_id = %s", (pro_id,))
        produto = cursor.fetchone()

        if not produto:
            flash("Produto não encontrado.", "danger")
            return redirect(url_for('listar_produtos'))

        cursor.close()

        return render_template('editar_produto.html', produto=produto)

    # Se for uma requisição POST, atualiza o produto
    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form['descricao']
        preco = request.form['precouni']
        quantidade = request.form['quantidade']

        # Atualiza o produto
        cursor.execute("""
            UPDATE tb_produtos 
            SET pro_nome = %s, pro_descricao = %s, pro_preco = %s, pro_quantidade = %s
            WHERE pro_id = %s
        """, (nome, descricao, preco, quantidade, pro_id))
        mysql.connection.commit()

        cursor.close()

        flash("Produto atualizado com sucesso!", "success")
        return redirect(url_for('listar_produtos'))



@app.route('/excluir_produto/<int:pro_id>', methods=['GET', 'POST'])
@login_required
def excluir_produto(pro_id):
    cursor = mysql.connection.cursor()
    
    # Excluir o produto
    cursor.execute("DELETE FROM tb_produtos WHERE pro_id = %s", (pro_id,))
    mysql.connection.commit()
    
    cursor.close()
    flash("Produto excluído com sucesso!", "success")
    return redirect(url_for('listar_produtos'))