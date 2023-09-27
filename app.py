import sqlite3
from flask import Flask, request, jsonify, abort

app = Flask(__name__)

def is_valid_string(value):
    """Verifica se a string contém apenas letras."""
    return all(c.isalpha() or c.isspace() for c in value)

class BancoDeDados:
    def __init__(self, nome_banco):
        self.nome_banco = nome_banco

    def conectar(self):
        try:
            conn = sqlite3.connect(self.nome_banco)
            return conn
        except sqlite3.Error as e:
            print("Falha na conexão com o SQLite.")
            return None

class Aluno:
    def __init__(self, conn):
        self.conn = conn

    def listar_alunos(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM alunos")
        alunos = [
            dict(id=row[0], nome=row[1], origem=row[2], destino=row[3])
            for row in cursor.fetchall()
        ]
        return alunos

    def criar_aluno(self, nome, origem, destino):
        if not (is_valid_string(nome) and is_valid_string(origem) and is_valid_string(destino)):
            abort(400, "Os campos devem conter apenas letras.")

        cursor = self.conn.cursor()
        sql = """INSERT INTO alunos (nome, origem, destino) VALUES (?, ?, ?)"""
        cursor.execute(sql, (nome, origem, destino))
        self.conn.commit()
        return cursor.lastrowid

    def buscar_aluno(self, id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM alunos WHERE id=?", (id,))
        aluno = cursor.fetchone()
        if aluno:
            return dict(id=aluno[0], nome=aluno[1], origem=aluno[2], destino=aluno[3])
        else:
            abort(404, "Aluno não encontrado.")

    def atualizar_aluno(self, id, nome, origem, destino):
        if not (is_valid_string(nome) and is_valid_string(origem) and is_valid_string(destino)):
            abort(400, "Os campos devem conter apenas letras.")

        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM alunos WHERE id=?", (id,))
        if not cursor.fetchone():
            abort(404, "Aluno não encontrado.")

        sql = """UPDATE alunos
                 SET nome=?, origem=?, destino=?
                 WHERE id=? """
        cursor.execute(sql, (nome, origem, destino, id))
        self.conn.commit()
        return dict(id=id, nome=nome, origem=origem, destino=destino)

    def deletar_aluno(self, id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM alunos WHERE id=?", (id,))
        if not cursor.fetchone():
            abort(404, "Aluno não encontrado.")

        sql = """DELETE FROM alunos WHERE id=?"""
        cursor.execute(sql, (id,))
        self.conn.commit()
        return f"O aluno com id: {id} foi deletado com sucesso."

@app.route('/alunos', methods=['GET', 'POST'])
def alunos_geral():
    banco = BancoDeDados("intercambio.sqlite")
    conn = banco.conectar()
    aluno = Aluno(conn)

    if request.method == 'GET':
        alunos = aluno.listar_alunos()
        return jsonify(alunos)

    if request.method == 'POST':
        new_name = request.form['nome']
        new_origin = request.form['origem']
        new_destination = request.form['destino']

        if not (is_valid_string(new_name) and is_valid_string(new_origin) and is_valid_string(new_destination)):
            return abort(400, "Os campos devem conter apenas letras.")

        aluno_id = aluno.criar_aluno(new_name, new_origin, new_destination)
        return f"Aluno com o id: {aluno_id} criado com sucesso"

@app.route('/aluno/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def aluno_por_id(id):
    banco = BancoDeDados("intercambio.sqlite")
    conn = banco.conectar()
    aluno = Aluno(conn)

    if request.method == 'GET':
        aluno_info = aluno.buscar_aluno(id)
        return jsonify(aluno_info), 200

    if request.method == 'PUT':
        nome = request.form['nome']
        origem = request.form['origem']
        destino = request.form['destino']

        if not (is_valid_string(nome) and is_valid_string(origem) and is_valid_string(destino)):
            abort(400, "Os campos devem conter apenas letras.")

        aluno_atualizado = aluno.atualizar_aluno(id, nome, origem, destino)
        return jsonify(aluno_atualizado)

    if request.method == 'DELETE':
        result = aluno.deletar_aluno(id)
        return result, 200

if __name__ == '__main__':
    app.run(port=5000, host='localhost', debug=True)
