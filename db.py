import sqlite3

conn = sqlite3.connect('intercambio.sqlite')

cursor = conn.cursor()
SQL_QUERY = """ CREATE TABLE alunos (
    id integer PRIMARY KEY,
    nome text NOT NULL,
    origem text NOT NULL,
    destino text NOT NULL
)"""
cursor.execute(SQL_QUERY)
