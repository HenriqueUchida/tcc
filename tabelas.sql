-- Habilita a extensão para cálculos matemáticos de similaridade facial
CREATE EXTENSION IF NOT EXISTS vector;

-- Armazena os moradores autorizados a entrar no micro mercado
CREATE TABLE usuarios (
    id_morador SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    status_ativo BOOLEAN DEFAULT TRUE,
    vetor_facial vector(128) -- Array de 128 posições gerado pela IA
);

-- Registra quem está no ambiente para posterior cruzamento com a balança
CREATE TABLE sessoes_tracking (
    id_sessao SERIAL PRIMARY KEY,
    id_morador INT REFERENCES moradores(id_morador),
    track_id INT NOT NULL,
    entrada TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    saida TIMESTAMP
);