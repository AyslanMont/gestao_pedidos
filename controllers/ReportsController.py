from gestao_pedidos import app
from gestao_pedidos.database.config import mysql
from flask import render_template, request, flash,redirect,url_for
from flask_login import login_required

@app.route('/relatorios', methods=['GET', 'POST'])
@login_required
def relatorios():
    resultado = None
    cursor = mysql.connection.cursor()

    if request.method == 'POST':
        filtro = request.form.get('filtro')

        try:
            if filtro == 'total_vendas_cliente':
                query = """
                    SELECT cli_nome, SUM(ped_total) AS total_vendas 
                    FROM tb_pedidos 
                    JOIN tb_clientes ON cli_id = ped_cli_id 
                    GROUP BY cli_nome
                """
                cursor.execute(query)
                resultado = cursor.fetchall()

            elif filtro == 'clientes_acima_1000':
                query = """
                    SELECT cli_nome, SUM(ped_total) AS total_vendas 
                    FROM tb_pedidos 
                    JOIN tb_clientes ON cli_id = ped_cli_id 
                    GROUP BY cli_nome 
                    HAVING total_vendas > 1000
                """
                cursor.execute(query)
                resultado = cursor.fetchall()

            elif filtro == 'top_produtos':
                query = """
                    SELECT pro_nome, SUM(proPed_qdproduto) AS qtd_total 
                    FROM tb_proPed 
                    JOIN tb_produtos ON proPed_pro_id = pro_id 
                    JOIN tb_pedidos ON proPed_ped_id = ped_id
                    WHERE ped_data BETWEEN DATE_SUB(NOW(), INTERVAL 30 DAY) AND NOW() 
                    GROUP BY pro_nome 
                    ORDER BY qtd_total DESC 
                    LIMIT 10
                """
                cursor.execute(query)
                resultado = cursor.fetchall()

            elif filtro == 'produtos_nao_vendidos':
                query = """
                    SELECT pro_nome 
                    FROM tb_produtos 
                    WHERE pro_id NOT IN (
                        SELECT proPed_pro_id 
                        FROM tb_proPed 
                        JOIN tb_pedidos ON proPed_ped_id = ped_id
                        WHERE ped_data BETWEEN DATE_SUB(NOW(), INTERVAL 30 DAY) AND NOW()
                    )
                """
                cursor.execute(query)
                resultado = cursor.fetchall()

            else:
                flash("Filtro inválido.", 'warning')
        except Exception as e:
            flash(f"Erro ao executar o filtro: {str(e)}", 'danger')
        finally:
            cursor.close()

    return render_template('relatorios.html', resultado=resultado)



@app.route('/logs_pedidos')
@login_required
def logs_pedidos():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM logs_pedidos ORDER BY data_hora DESC")
    logs = cursor.fetchall()
    cursor.close()

    return render_template('logs.html', logs=logs)