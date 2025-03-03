from gestao_pedidos.database.config import mysql

class Log:
    def __init__(self, id_log, operacao, log_ped_id, log_cli_id, data_hora):
        self.id_log = id_log
        self.operacao = operacao
        self.log_ped_id = log_ped_id
        self.log_cli_id = log_cli_id
        self.data_hora = data_hora

    @staticmethod
    def get_all_logs():
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM logs_pedidos ORDER BY data_hora DESC")
        logs = cursor.fetchall()
        cursor.close()
        return logs
