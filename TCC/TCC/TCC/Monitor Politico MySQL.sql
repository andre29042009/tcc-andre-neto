CREATE DATABASE monitor_politico;
USE monitor_politico;

CREATE TABLE politicos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    cargo VARCHAR(100) NOT NULL,
    partido VARCHAR(50),
    uf CHAR(2),
    desde YEAR
);

CREATE TABLE temas_promessas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tema VARCHAR(100) NOT NULL
);

CREATE TABLE promessas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    politico_id INT NOT NULL,
    tema_id INT NOT NULL,
    descricao TEXT NOT NULL,

    FOREIGN KEY (politico_id)
        REFERENCES politicos(id),

    FOREIGN KEY (tema_id)
        REFERENCES temas_promessas(id)
);

CREATE TABLE sites (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    url VARCHAR(500) NOT NULL
);

CREATE TABLE seletores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    site_id INT NOT NULL,
    seletor VARCHAR(100) NOT NULL,

    FOREIGN KEY (site_id)
        REFERENCES sites(id)
);

CREATE TABLE noticias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    promessa_id INT NOT NULL,
    site_id INT NOT NULL,
    titulo VARCHAR(300),
    link VARCHAR(500),
    data_publicacao DATE,

    FOREIGN KEY (promessa_id)
        REFERENCES promessas(id),

    FOREIGN KEY (site_id)
        REFERENCES sites(id)
);