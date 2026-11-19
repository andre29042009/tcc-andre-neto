USE monitor_politico;

-- --------------------------------------------------------
-- 1. Inserindo Temas das Promessas
-- --------------------------------------------------------
INSERT INTO temas_promessas (tema) VALUES 
('saúde pública'),
('educação'),
('segurança pública'),
('emprego e renda'),
('infraestrutura'),
('meio ambiente'),
('habitação e moradia'),
('transporte e mobilidade'),
('assistência social'),
('economia e desenvolvimento'),
('saneamento básico'),
('administração pública');


-- --------------------------------------------------------
-- 2. Inserindo Fontes/Sites baseados no Scraper do Python
-- --------------------------------------------------------
INSERT INTO sites (nome, url) VALUES 
('Google Notícias', 'https://news.google.com/'),
('Câmara dos Deputados', 'https://www.camara.leg.br/'),
('Senado Federal', 'https://www25.senado.leg.br/'),
('Agência Brasil', 'https://agenciabrasil.ebc.com.br/');


-- --------------------------------------------------------
-- 3. Inserindo Políticos
-- --------------------------------------------------------

-- Esfera Federal
INSERT INTO politicos (nome, cargo, partido, uf, desde) VALUES 
('Luiz Inácio Lula da Silva', 'Presidente da República', 'PT', 'BR', 2023),
('Geraldo Alckmin', 'Vice-Presidente', 'PSB', 'BR', 2023),
('Rodrigo Pacheco', 'Presidente do Senado', 'PSD', 'MG', 2021),
('Arthur Lira', 'Presidente da Câmara', 'PP', 'AL', 2021),
('Fernando Haddad', 'Min. Fazenda', 'PT', 'SP', 2023),
('Flávio Dino', 'Min. STF / ex-Min. Justiça', 'PSB', 'MA', 2023),
('Simone Tebet', 'Min. Planejamento', 'MDB', 'MS', 2023),
('Alexandre Silveira', 'Min. Minas e Energia', 'PSD', 'MG', 2023);

-- Governadores
INSERT INTO politicos (nome, cargo, partido, uf, desde) VALUES 
('Gladson Cameli', 'Governador', 'PP', 'AC', 2019),
('Paulo Dantas', 'Governador', 'MDB', 'AL', 2022),
('Wilson Lima', 'Governador', 'União Brasil', 'AM', 2019),
('Clécio Luís', 'Governador', 'Solidariedade', 'AP', 2023),
('Jerônimo Rodrigues', 'Governador', 'PT', 'BA', 2023),
('Elmano de Freitas', 'Governador', 'PT', 'CE', 2023),
('Ibaneis Rocha', 'Governador', 'MDB', 'DF', 2019),
('Renato Casagrande', 'Governador', 'PSB', 'ES', 2019),
('Ronaldo Caiado', 'Governador', 'União Brasil', 'GO', 2019),
('Carlos Brandão', 'Governador', 'PSB', 'MA', 2023),
('Romeu Zema', 'Governador', 'Novo', 'MG', 2019),
('Eduardo Riedel', 'Governador', 'PSDB', 'MS', 2023),
('Mauro Mendes', 'Governador', 'União Brasil', 'MT', 2019),
('Helder Barbalho', 'Governador', 'MDB', 'PA', 2019),
('João Azevêdo', 'Governador', 'PSB', 'PB', 2019),
('Raquel Lyra', 'Governadora', 'PSDB', 'PE', 2023),
('Rafael Fonteles', 'Governador', 'PT', 'PI', 2023),
('Ratinho Junior', 'Governador', 'PSD', 'PR', 2019),
('Cláudio Castro', 'Governador', 'PL', 'RJ', 2021),
('Fátima Bezerra', 'Governadora', 'PT', 'RN', 2019),
('Marcos Rocha', 'Governador', 'União Brasil', 'RO', 2019),
('Arthur Henrique', 'Governador', 'MDB', 'RR', 2023),
('Eduardo Leite', 'Governador', 'PSDB', 'RS', 2019),
('Jorginho Mello', 'Governador', 'PL', 'SC', 2023),
('Fábio Mitidieri', 'Governador', 'PSD', 'SE', 2023),
('Tarcísio de Freitas', 'Governador', 'Republicanos', 'SP', 2023),
('Wanderlei Barbosa', 'Governador', 'Republicanos', 'TO', 2022);

-- Prefeitos
INSERT INTO politicos (nome, cargo, partido, uf, desde) VALUES 
('Alysson Bestene', 'Prefeito', 'PP', 'AC', 2026),
('Rodrigo Cunha', 'Prefeito', 'Podemos', 'AL', 2026),
('Pedro dos Santos Martins', 'Prefeito', 'União Brasil', 'AP', 2026),
('David Almeida', 'Prefeito', 'Avante', 'AM', 2021),
('Bruno Reis', 'Prefeito', 'União Brasil', 'BA', 2021),
('Evandro Leitão', 'Prefeito', 'PT', 'CE', 2025),
('Celina Leão', 'Governadora (acumula funções de Prefeita)', 'PP', 'DF', 2026),
('Cris Samorini', 'Prefeita', 'PP', 'ES', 2026),
('Sandro Mabel', 'Prefeito', 'União Brasil', 'GO', 2025),
('Esmênia Miranda', 'Prefeita', 'PSD', 'MA', 2026),
('Abilio Brunini', 'Prefeito', 'PL', 'MT', 2025),
('Rose Modesto', 'Prefeita', 'Independente', 'MS', 2024),
('Álvaro Damião', 'Prefeito', 'União Brasil', 'MG', 2025),
('Igor Normando', 'Prefeito', 'MDB', 'PA', 2025),
('Leo Bezerra', 'Prefeito', 'PSB', 'PB', 2026),
('Eduardo Pimentel', 'Prefeito', 'PSD', 'PR', 2025),
('João Campos', 'Prefeito', 'PSB', 'PE', 2021),
('Silvio Mendes', 'Prefeito', 'União Brasil', 'PI', 2025),
('Eduardo Cavaliere', 'Prefeito', 'PSD', 'RJ', 2026),
('Paulinho Freire', 'Prefeito', 'União Brasil', 'RN', 2025),
('Sebastião Melo', 'Prefeito', 'MDB', 'RS', 2021),
('Léo Moraes', 'Prefeito', 'Podemos', 'RO', 2025),
('Marcelo Zeitoune', 'Prefeito', 'PL', 'RR', 2026),
('Topázio Neto', 'Prefeito', 'Podemos', 'SC', 2022),
('Ricardo Nunes', 'Prefeito', 'MDB', 'SP', 2021),
('Emília Corrêa', 'Prefeita', 'PL', 'SE', 2025),
('Eduardo Siqueira Campos', 'Prefeito', 'Podemos', 'TO', 2025);