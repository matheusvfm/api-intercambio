"""Importa as funções do banco de dados"""
import sqlite3
#import json
from flask import Flask, request, jsonify

app = Flask(__name__)

def db_connection():
    """Connect to database"""
    conn = None
    try:
        conn = sqlite3.connect("intercambio.sqlite")
    except sqlite3.error:
        print("Falha na conexão com o sqlite.")
    return conn

@app.route('/alunos',methods=['GET', 'POST'])
def alunos_geral():
    """Consultar(todos)/Criar aluno(s)"""
    conn = db_connection()
    cursor = conn.cursor()

    if request.method == 'GET':
        cursor = conn.execute("SELECT * FROM alunos")
        alunos = [
            dict(id=row[0], nome=row[1], origem=row[2], destino=row[3])
            for row in cursor.fetchall()
        ]
        if alunos is not None:
            return jsonify(alunos)

    if request.method == 'POST':
        new_name = request.form['nome']
        new_origin = request.form['origem']
        new_destinination = request.form['destino']
        sql = """INSERT INTO alunos (nome, origem, destino)
                 VALUES (?, ?, ?)"""
        cursor = cursor.execute(sql, (new_name, new_origin, new_destinination))
        conn.commit()
        return f"Aluno com o id: {cursor.lastrowid} criado com sucesso"
    return None

# Consultar/Editar/Excluir(id)
@app.route('/aluno/<int:id>',methods=['GET', 'PUT', 'DELETE'])

def aluno_por_id(id):
    """Busca, edita, exclui aluno por id"""
    conn = db_connection()
    cursor = conn.cursor()
    aluno = None

    if request.method == 'GET':
        cursor.execute("SELECT * FROM alunos where id=?", (id,))
        rows = cursor.fetchall()
        for row in rows:
            aluno = row
        if aluno is not None:
            return jsonify(aluno), 200
        return "Algo deu errado", 404

    if request.method == 'PUT':
        sql = """UPDATE alunos
                SET nome=?,
                    origem=?,
                    destino=?
                where id=? """

        nome = request.form['nome']
        origem = request.form['origem']
        destino = request.form['destino']
        aluno_atualizado = {
                'id': id,
                'nome': nome,
                'origem': origem,
                'destino': destino,
        }
        conn.execute(sql, (nome,  origem, destino, id))
        conn.commit()
        return jsonify(aluno_atualizado)

    if request.method == 'DELETE':
        sql = """ DELETE FROM alunos where id=? """
        conn.execute(sql, (id,))
        conn.commit()
        return f"O aluno com id: {id} foi deletado com sucesso.",200
    return None

app.run(port=5000,host='localhost',debug=True)
