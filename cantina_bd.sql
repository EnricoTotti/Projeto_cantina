-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Tempo de geração: 23/06/2025 às 19:59
-- Versão do servidor: 10.4.32-MariaDB
-- Versão do PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Banco de dados: `cantina`
--
CREATE DATABASE IF NOT EXISTS `cantina` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `cantina`;

-- --------------------------------------------------------

--
-- Estrutura para tabela `itens_venda`
--

CREATE TABLE `itens_venda` (
  `cod_itens_venda` int(4) NOT NULL,
  `qtde` int(4) DEFAULT NULL,
  `valor_unico` decimal(7,2) DEFAULT NULL,
  `cod_produto` int(4) DEFAULT NULL,
  `cod_venda` int(6) DEFAULT NULL,
  `data_cadastro` datetime DEFAULT current_timestamp(),
  `status` bit(1) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Despejando dados para a tabela `itens_venda`
--

INSERT INTO `itens_venda` (`cod_itens_venda`, `qtde`, `valor_unico`, `cod_produto`, `cod_venda`, `data_cadastro`, `status`) VALUES
(21, 2, 6.00, 15, 18, '2025-06-23 14:48:26', b'1'),
(22, 1, 5.00, 14, 18, '2025-06-23 14:48:26', b'1'),
(23, 3, 3.00, 16, 19, '2025-06-23 14:50:34', b'1'),
(24, 1, 3.00, 17, 19, '2025-06-23 14:50:34', b'1'),
(25, 1, 5.00, 14, 19, '2025-06-23 14:50:34', b'1'),
(26, 1, 3.00, 15, 19, '2025-06-23 14:50:34', b'1');

-- --------------------------------------------------------

--
-- Estrutura para tabela `produto`
--

CREATE TABLE `produto` (
  `cod_produto` int(4) NOT NULL,
  `nome` varchar(50) DEFAULT NULL,
  `preco` decimal(7,2) DEFAULT NULL,
  `data_cadastro` datetime DEFAULT current_timestamp(),
  `status` bit(1) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Despejando dados para a tabela `produto`
--

INSERT INTO `produto` (`cod_produto`, `nome`, `preco`, `data_cadastro`, `status`) VALUES
(14, 'Salgado médio', 5.00, '2025-06-23 13:20:53', b'1'),
(15, 'Suco', 3.00, '2025-06-23 14:46:50', b'1'),
(16, 'Paçoca', 1.00, '2025-06-23 14:49:26', b'1'),
(17, 'Bolo', 3.00, '2025-06-23 14:49:36', b'0');

-- --------------------------------------------------------

--
-- Estrutura para tabela `venda`
--

CREATE TABLE `venda` (
  `cod_venda` int(6) NOT NULL,
  `valor_total` decimal(7,2) DEFAULT NULL,
  `forma_pagamento` varchar(7) DEFAULT NULL,
  `data_cadastro` datetime DEFAULT current_timestamp(),
  `status` bit(1) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Despejando dados para a tabela `venda`
--

INSERT INTO `venda` (`cod_venda`, `valor_total`, `forma_pagamento`, `data_cadastro`, `status`) VALUES
(18, 11.00, 'Crédito', '2025-06-23 14:48:26', b'1'),
(19, 14.00, 'Crédito', '2022-06-23 14:50:34', b'1');

--
-- Índices para tabelas despejadas
--

--
-- Índices de tabela `itens_venda`
--
ALTER TABLE `itens_venda`
  ADD PRIMARY KEY (`cod_itens_venda`),
  ADD KEY `cod_produto` (`cod_produto`),
  ADD KEY `cod_venda` (`cod_venda`);

--
-- Índices de tabela `produto`
--
ALTER TABLE `produto`
  ADD PRIMARY KEY (`cod_produto`);

--
-- Índices de tabela `venda`
--
ALTER TABLE `venda`
  ADD PRIMARY KEY (`cod_venda`);

--
-- AUTO_INCREMENT para tabelas despejadas
--

--
-- AUTO_INCREMENT de tabela `itens_venda`
--
ALTER TABLE `itens_venda`
  MODIFY `cod_itens_venda` int(4) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=27;

--
-- AUTO_INCREMENT de tabela `produto`
--
ALTER TABLE `produto`
  MODIFY `cod_produto` int(4) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=18;

--
-- AUTO_INCREMENT de tabela `venda`
--
ALTER TABLE `venda`
  MODIFY `cod_venda` int(6) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=20;

--
-- Restrições para tabelas despejadas
--

--
-- Restrições para tabelas `itens_venda`
--
ALTER TABLE `itens_venda`
  ADD CONSTRAINT `itens_venda_ibfk_1` FOREIGN KEY (`cod_produto`) REFERENCES `produto` (`cod_produto`),
  ADD CONSTRAINT `itens_venda_ibfk_2` FOREIGN KEY (`cod_venda`) REFERENCES `venda` (`cod_venda`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
