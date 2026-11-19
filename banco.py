import sqlite3
from pathlib import Path

CAMINHO_BANCO = Path(__file__).resolve().parent / "banco.db"


def obter_conexao():
    conexao = sqlite3.connect(CAMINHO_BANCO)
    conexao.row_factory = sqlite3.Row
    return conexao


def inicializar_banco():
    """Cria o arquivo SQLite e a tabela de contas se ainda não existirem."""
    with obter_conexao() as conexao:
        conexao.execute(
            """
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT NOT NULL UNIQUE,
                senha_hash TEXT NOT NULL
            )
            """
        )
