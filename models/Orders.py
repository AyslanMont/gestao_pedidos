from gestao_pedidos.database.config import mysql

class Orders:
    def __init__(self, cli_id, data, total, produtos):
        self.cli_id = cli_id
        self.data = data
        self.total = total
        self.produtos = produtos

    def save(self):
        cursor = mysql.connection.cursor()

        # Verificar se o pedido já existe
        cursor.execute(
            "SELECT * FROM tb_pedidos WHERE ped_data = %s AND ped_cli_id = %s",
            (self.data, self.cli_id),
        )
        pedido = cursor.fetchone()

        if pedido:
            cursor.close()
            return {"success": False, "message": "O pedido já está cadastrado!"}

        # Inserir o novo pedido
        cursor.execute(
            "INSERT INTO tb_pedidos (ped_data, ped_cli_id, ped_total) VALUES (%s, %s, %s)",
            (self.data, self.cli_id, self.total),
        )
        pedido_id = cursor.lastrowid

        # Inserir os produtos do pedido
        for produto in self.produtos:
            cursor.execute(
                "INSERT INTO tb_proPed (proPed_ped_id, proPed_pro_id, proPed_qdproduto, proPed_subtotal) VALUES (%s, %s, %s, %s)",
                (pedido_id, produto['pro_id'], produto['quantidade'], produto['subtotal']),
            )

        mysql.connection.commit()
        cursor.close()

        return {"success": True, "message": "Pedido cadastrado com sucesso!"}

    @staticmethod
    def calcular_total_pedido(pedido_id):
        cursor = mysql.connection.cursor()
        cursor.execute("""
            SELECT SUM(proPed_subtotal) AS total 
            FROM tb_proPed 
            WHERE proPed_ped_id = %s
        """, (pedido_id,))
        total = cursor.fetchone()['total']
        cursor.close()
        return total

    @staticmethod
    def get_all(ordem='asc'):
        query = f'''
            SELECT 
                ped_id, 
                ped_data, 
                cli_nome, 
                ped_total,
                GROUP_CONCAT(pro_nome SEPARATOR ', ') AS produtos
            FROM 
                tb_pedidos
            JOIN 
                tb_clientes 
            ON 
                ped_cli_id = cli_id 
            JOIN 
                tb_proPed 
            ON 
                ped_id = proPed_ped_id
            JOIN 
                tb_produtos 
            ON 
                proPed_pro_id = pro_id
            GROUP BY 
                ped_id, ped_data, cli_nome,ped_total
            ORDER BY 
                ped_data {"ASC" if ordem == "asc" else "DESC"}
        '''
        cursor = mysql.connection.cursor()
        cursor.execute(query)
        dados = cursor.fetchall()
        cursor.close()
        return dados