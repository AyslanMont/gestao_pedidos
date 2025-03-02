
CREATE DATABASE IF NOT EXISTS db_pedidos;
USE db_pedidos;

-- Tabela de Clientes
CREATE TABLE IF NOT EXISTS tb_clientes (
    cli_id INT AUTO_INCREMENT PRIMARY KEY,
    cli_nome VARCHAR(100) NOT NULL,
    cli_email VARCHAR(255) NOT NULL UNIQUE,
    cli_telefone VARCHAR(15) NOT NULL,
    cli_endereco TEXT NOT NULL
);

-- Tabela de Produtos
CREATE TABLE IF NOT EXISTS tb_produtos (
    pro_id INT AUTO_INCREMENT PRIMARY KEY,
    pro_nome VARCHAR(200) NOT NULL,
    pro_desc TEXT NOT NULL,
    pro_quantidade INT NOT NULL,
    pro_preco DECIMAL(10,2) NOT NULL
);

-- Tabela de Pedidos
CREATE TABLE IF NOT EXISTS tb_pedidos (
    ped_id INT AUTO_INCREMENT PRIMARY KEY,
    ped_cli_id INT NOT NULL,
    ped_data DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ped_total DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (ped_cli_id) REFERENCES tb_clientes(cli_id) ON DELETE CASCADE
);

-- Tabela de Produtos por Pedido
CREATE TABLE IF NOT EXISTS tb_proPed (
    proPed_id INT AUTO_INCREMENT PRIMARY KEY,
    proPed_ped_id INT NOT NULL,
    proPed_pro_id INT NOT NULL,
    proPed_qdproduto INT NOT NULL,
    proPed_subtotal DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (proPed_ped_id) REFERENCES tb_pedidos(ped_id),
    FOREIGN KEY (proPed_pro_id) REFERENCES tb_produtos(pro_id)
);

-- Tabela de Usuários
CREATE TABLE IF NOT EXISTS tb_usuarios (
    usu_id INT AUTO_INCREMENT PRIMARY KEY,
    usu_nome VARCHAR(150) NOT NULL,
    usu_email VARCHAR(150) NOT NULL,
    usu_senha VARCHAR(500) NOT NULL,
    usu_tipo ENUM('admin', 'user') DEFAULT 'user'
);

-- Tabela de Logs de Pedidos
CREATE TABLE IF NOT EXISTS logs_pedidos (
    id_log INT AUTO_INCREMENT PRIMARY KEY,
    operacao VARCHAR(10) NOT NULL,
    log_ped_id INT NOT NULL,
    log_cli_id INT NOT NULL,
    data_hora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de para admin
CREATE TABLE IF NOT EXISTS tb_admin (
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    admin_nome VARCHAR(150) NOT NULL,
    admin_email VARCHAR(150) NOT NULL UNIQUE,
    admin_senha VARCHAR(500) NOT NULL
);



-- Trigger para registrar logs de pedidos
DELIMITER //
CREATE TRIGGER log_pedidos AFTER INSERT ON tb_pedidos
FOR EACH ROW
BEGIN
    INSERT INTO logs_pedidos (operacao, id_pedido, id_cliente, usuario, data_hora)
    VALUES ('INSERT', NEW.ped_id, NEW.ped_cli_id, CURRENT_USER(), NOW());
END //
DELIMITER ;

-- Trigger para atualizar o estoque
DELIMITER //
CREATE TRIGGER atualizar_estoque AFTER INSERT ON tb_proPed
FOR EACH ROW
BEGIN
    UPDATE tb_produtos 
    SET pro_quantidade = pro_quantidade - NEW.proPed_qdproduto 
    WHERE pro_id = NEW.proPed_pro_id;
END //
DELIMITER ;

-- Procedimento para validar pedidos
DELIMITER //
CREATE PROCEDURE validar_pedido(IN id_cliente INT, IN id_produto INT, IN quantidade INT)
BEGIN
    DECLARE estoque_atual INT;
    SELECT pro_quantidade INTO estoque_atual FROM tb_produtos WHERE pro_id = id_produto;
    IF estoque_atual >= quantidade THEN
        SELECT TRUE AS valido;
    ELSE
        SELECT FALSE AS valido;
    END IF;
END //
DELIMITER ;


select * from tb_admin;

